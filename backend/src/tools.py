import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from supabase import create_client, Client
from crewai_tools import SerperDevTool

load_dotenv()

serper_tool_instance = SerperDevTool(
    search_url="https://google.serper.dev/news",
    n_results=5,
    country="br",
    locale="pt-br",
    location="Sao Paulo, Brazil",
    tbs="qdr:d"
)

class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = (
        "Busca notícias, esportes e fatos recentes na internet. "
        "PROIBIDO: Não use para buscar taxas da InfinitePay (use a doc oficial)."
    )

    def _run(self, query: str) -> str:
        try:
            return serper_tool_instance.run(search_query=query)
        except Exception as e:
            return f"Erro na busca web: {str(e)}"


class InfinitePayKnowledgeTool(BaseTool):
    name: str = "InfinitePay Documentation Search"
    description: str = (
        "FONTE OFICIAL para responder sobre taxas, maquininhas, planos e produtos. "
        "Busca vetorial na base de conhecimento da empresa."
    )

    def _run(self, query: str) -> str:
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004", 
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
            query_vector = embeddings.embed_query(query)
            
            supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

            response = supabase.rpc("match_documents", {
                "query_embedding": query_vector, 
                "match_threshold": 0.3, 
                "match_count": 4, 
                "filter": {}
            }).execute()

            if not response.data:
                return "Nenhuma informação encontrada na documentação oficial sobre este tópico."
            
            return "\n\n".join([f"---\n{d['content']}" for d in response.data])

        except Exception as e:
            return f"Erro RAG: {str(e)}"

class TransactionStatusTool(BaseTool):
    name: str = "Check Transaction Status"
    description: str = "Investiga falhas em vendas e histórico financeiro. Entrada: user_id."

    def _run(self, user_id: str) -> str:
        try:
            supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            res = supabase.table("transactions").select("*").eq("user_id", user_id).order("date", desc=True).limit(3).execute()
            
            if not res.data:
                return json.dumps({"status": "no_data", "message": "Nenhuma transação encontrada."}, indent=2)
            
            return json.dumps(res.data, indent=2, default=str)
        except Exception as e:
            return f"Erro DB: {e}"

class AccountDetailsTool(BaseTool):
    name: str = "Check Account Details"
    description: str = "Verifica status cadastral da conta. Entrada: user_id."

    def _run(self, user_id: str) -> str:
        try:
            supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            res = supabase.table("users").select("*").eq("user_id", user_id).execute()
            
            if not res.data:
                return "Usuário não encontrado."
            
            u = res.data[0]
            return f"Cliente: {u['name']} | Status da Conta: {u['account_status']} | Email: {u.get('email', 'N/A')}"
        except Exception as e:
            return f"Erro DB: {e}"


class DelegateToKnowledgeTool(BaseTool):
    name: str = "Call Knowledge Agent"
    description: str = "Delegar perguntas sobre Taxas, Produtos ou Notícias. Entrada: A pergunta do usuário."

    def _run(self, question: str) -> str:
        llm = LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
        
        agent = Agent(
            role='Knowledge Specialist',
            goal='Responder com precisão absoluta e formatação visual impecável.',
            backstory=(
                "Você é o especialista em comunicação da InfinitePay. \n"
                "Sua prioridade número 1 é a clareza visual. \n"
                "DIRETRIZES:\n"
                "1. Se houver números e categorias, OBRIGATORIAMENTE use Tabela Markdown.\n"
                "2. Não liste itens soltos linha por linha.\n"
                "3. Se a pergunta for sobre InfinitePay, use a 'InfinitePay Documentation Search'.\n"
                "4. Se a pergunta for sobre futebol/mundo, use a 'Web Search Tool'.\n"
            ),
            tools=[InfinitePayKnowledgeTool(), WebSearchTool()],
            llm=llm,
            verbose=True
        )
        
        task = Task(
            description=(
                f"Analise a pergunta: '{question}'.\n"
                "1. Identifique o idioma e responda no mesmo idioma.\n"
                "2. Busque os dados.\n"
                "3. GERE UMA TABELA MARKDOWN se houver taxas ou listas de valores.\n"
                "4. Inclua o link da fonte no final."
            ),
            agent=agent,
            expected_output="Uma resposta estruturada, preferencialmente com tabelas para dados numéricos."
        )
        
        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        return str(crew.kickoff())

class DelegateToSupportTool(BaseTool):
    name: str = "Call Support Agent"
    description: str = "Delegar problemas de Conta/Erro/Login. Entrada OBRIGATÓRIA: 'user_id|pergunta'."

    def _run(self, input_str: str) -> str:
        try:
            if "|" not in input_str:
                return "Erro de Uso da Tool: O input deve ser 'user_id|pergunta'."
            user_id, question = input_str.split("|", 1)
        except:
            return "Erro de formato. Use: user_id|pergunta"

        llm = LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
        
        agent = Agent(
            role='Support Specialist',
            goal='Ler os dados brutos (JSON) e relatar EXATAMENTE a quantidade de itens encontrados.',
            backstory=(
                "Você é um auditor de dados. Você recebe um JSON bruto do banco de dados.\n"
                "Sua regra absoluta: Se o JSON tem 1 item, você fala de 1 item.\n"
                "Se o JSON tem 5 itens, você fala de 5 itens.\n"
                "JAMAIS invente dados para preencher espaço. Seja fiel ao JSON."
            ),
            tools=[TransactionStatusTool(), AccountDetailsTool()],
            llm=llm,
            verbose=True
        )
        
        task = Task(
            description=(
                f"O usuário '{user_id}' perguntou: '{question}'.\n"
                "1. Chame a ferramenta de transações.\n"
                "2. Você receberá uma lista em JSON (ex: `[{{...}}, {{...}}]`).\n"
                "3. CONTE quantos objetos existem na lista.\n" # <--- Instrução de contagem
                "4. Liste apenas esses objetos. Se a lista tiver apenas 1, liste apenas 1.\n"
                "5. Explique o motivo de falhas se houver."
            ),
            agent=agent,
            expected_output=(
                "Um resumo falado fiel aos dados do JSON em MARKDOWN sem a formatação do JSON"
            )
        )
        
        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        return str(crew.kickoff())