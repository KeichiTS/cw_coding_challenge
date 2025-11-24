import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
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
        "PROIBIDO: Não use para buscar taxas da InfinitePay."
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
        "Se não estiver aqui, a informação não existe."
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
                return "Nada encontrado na doc oficial."
            
            return "\n\n".join([f"---\n{d['content']}" for d in response.data])

        except Exception as e:
            return f"Erro RAG: {str(e)}"

class TransactionStatusTool(BaseTool):
    name: str = "Check Transaction Status"
    description: str = "Investiga falhas em vendas. Entrada: user_id."

    def _run(self, user_id: str) -> str:
        try:
            supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            res = supabase.table("transactions").select("*").eq("user_id", user_id).order("date", desc=True).limit(3).execute()
            
            if not res.data:
                return "Nenhuma transação encontrada."
            
            report = "--- HISTÓRICO RECENTE ---\n"
            for t in res.data:
                report += f"Data: {t['date']} | Valor: {t['amount']} | Status: {t['status']} | Motivo: {t.get('reason_failure', '-')}\n"
            return report
        except Exception as e:
            return f"Erro DB: {e}"

class AccountDetailsTool(BaseTool):
    name: str = "Check Account Details"
    description: str = "Verifica status da conta. Entrada: user_id."

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
    description: str = "Delegar perguntas sobre Taxas, Produtos ou Notícias. Entrada: A pergunta."

    def _run(self, question: str) -> str:
        llm = LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
        
        agent = Agent(
            role='Knowledge Agent',
            goal='Responder a pergunta usando RAG ou Web Search.',
            backstory='Especialista em produtos InfinitePay e conhecimentos gerais.',
            tools=[InfinitePayKnowledgeTool(), WebSearchTool()],
            llm=llm,
            verbose=True
        )
        
        task = Task(
            description=f"Responda a pergunta: '{question}'.",
            agent=agent,
            expected_output="Resposta completa."
        )
        
        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        return str(crew.kickoff())

class DelegateToSupportTool(BaseTool):
    name: str = "Call Support Agent"
    description: str = "Delegar problemas de Conta/Erro. Entrada: 'user_id|pergunta'."

    def _run(self, input_str: str) -> str:
        try:
            user_id, question = input_str.split("|", 1)
        except:
            return "Erro de formato. Use: user_id|pergunta"

        llm = LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
        
        agent = Agent(
            role='Support Agent',
            goal='Resolver problemas de conta.',
            backstory='Suporte Técnico Nível 2 com acesso ao banco de dados.',
            tools=[TransactionStatusTool(), AccountDetailsTool()],
            llm=llm,
            verbose=True
        )
        
        task = Task(
            description=f"Analise '{question}' para o usuário '{user_id}'.",
            agent=agent,
            expected_output=(
                "Um relatório técnico baseado ESTRITAMENTE nos dados retornados pela ferramenta. "
                "Se a ferramenta retornar 'Usuário não encontrado' ou erro, "
                "responda APENAS: 'Não foi possível localizar os dados da conta para este ID'. "
                "JAMAIS invente dados."
            )
        )
        
        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        return str(crew.kickoff())