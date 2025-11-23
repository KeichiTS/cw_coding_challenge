import os
from dotenv import load_dotenv
from supabase import create_client, Client
from crewai.tools import BaseTool
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

class KnowledgeBaseTool(BaseTool):
    name: str = "InfinitePay Knowledge Base"
    description: str = (
        "Utilize para buscar informações oficiais sobre taxas, maquininhas, planos "
        "e documentação geral da InfinitePay. Entrada: A pergunta do usuário."
    )

    def _run(self, query: str) -> str:
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004", 
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
            query_vector = embeddings.embed_query(query)

            supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

            response = supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_vector,
                    "match_threshold": 0.3, 
                    "match_count": 4,
                    "filter": {}
                }
            ).execute()

            if not response.data:
                return "A busca na base de conhecimento não retornou nenhum resultado relevante."

            results = [f"**TRECHO DO MANUAL**\n{doc['content']}" for doc in response.data]
            return "\n\n".join(results)

        except Exception as e:
            return f"Erro técnico ao buscar na knowledge base: {str(e)}"

class CustomerSupportTool(BaseTool):
    name: str = "Customer Database Tool"
    description: str = (
        "Utilize SOMENTE para problemas de conta, transações ou cadastro. "
        "Entrada obrigatória: O 'user_id' do cliente."
    )

    def _run(self, user_id: str) -> str:
        try:
            supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            
            user_res = supabase.table("users").select("*").eq("user_id", user_id).execute()
            if not user_res.data:
                return f"Erro: Usuário com ID '{user_id}' não encontrado no banco."

            user = user_res.data[0]

            trans_res = supabase.table("transactions") \
                .select("*").eq("user_id", user_id) \
                .order("date", desc=True).limit(1).execute()
            
            last_trans = trans_res.data[0] if trans_res.data else {"status": "Nenhuma transação", "reason_failure": "-"}

            return f"""
            --- DADOS DO CLIENTE (CONFIDENCIAL) ---
            Nome: {user.get('name')}
            Status da Conta: {user.get('account_status')}
            Última Transação: {last_trans.get('status')}
            Motivo Falha: {last_trans.get('reason_failure')}
            """
        except Exception as e:
            return f"Erro ao consultar banco de clientes: {str(e)}"