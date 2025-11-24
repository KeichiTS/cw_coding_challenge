from crewai import Agent, LLM
from src.tools import (
    DelegateToKnowledgeTool,
    DelegateToSupportTool,
    InfinitePayKnowledgeTool, 
    TransactionStatusTool, 
    AccountDetailsTool,
    serper_tool_instance
)
import os
from dotenv import load_dotenv 


load_dotenv()


class InfinitePayAgents:
    def __init__(self):
        self.llm = LLM(
            model="gemini/gemini-2.5-flash", 
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def router_agent(self):
        return Agent(
            role='Router Agent',
            goal='Usar as ferramentas de chamada para redirecionar a pergunta.',
            backstory= "Você é um agente delegador. Você não resolve nada. Você apenas escolhe a ferramenta certa e repassa o texto.",
            allow_delegation=False,
            tools=[DelegateToKnowledgeTool(), DelegateToSupportTool()],
            verbose=True,
            llm=self.llm
        )

    def knowledge_agent(self):
        return Agent(
            role='Knowledge Agent',
            goal='Fornecer informações precisas usando a documentação oficial ou busca web.',
            backstory="Você é o especialista em produtos e informações gerais. Use suas ferramentas para buscar a verdade.",
            tools=[InfinitePayKnowledgeTool(), serper_tool_instance],
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def support_agent(self):
        return Agent(
            role='Support Agent',
            goal='Resolver problemas técnicos e de conta verificando dados do cliente.',
            backstory="Você é o suporte nível 2. Você lida com falhas, bloqueios e status.",
            tools=[TransactionStatusTool(), AccountDetailsTool()],
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )