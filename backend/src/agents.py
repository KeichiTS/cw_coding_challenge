from crewai import Agent, LLM
from src.tools import KnowledgeBaseTool, CustomerSupportTool
import os
from dotenv import load_dotenv 

load_dotenv()

class InfinitePayAgents:
    def __init__(self):
        self.llm = LLM(
            model="gemini/gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def universal_agent(self):
        knowledge_tool = KnowledgeBaseTool()
        support_tool = CustomerSupportTool()

        return Agent(
            role='InfinitePay Assistant',
            goal='Resolver a dúvida do usuário utilizando a ferramenta correta.',
            backstory=(
                "Você é o assistente oficial da InfinitePay. Você é inteligente e autônomo. "
                "Você tem acesso a duas ferramentas poderosas:\n"
                "1. 'InfinitePay Knowledge Base': Para qualquer dúvida sobre taxas, como funciona, preços.\n"
                "2. 'Customer Database Tool': Para verificar problemas na conta de um cliente específico.\n\n"
                "SEU PROCESSO DE PENSAMENTO:\n"
                "- O usuário perguntou sobre taxas? -> Uso a Knowledge Base.\n"
                "- O usuário reclamou de erro/conta? -> Verifico se tenho o ID. Se tiver, uso a Database Tool.\n"
                "Responda sempre de forma cordial e em Português."
            ),
            tools=[knowledge_tool, support_tool],
            verbose=True,
            allow_delegation=False, 
            llm=self.llm
        )