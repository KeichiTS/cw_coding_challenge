from crewai import Agent, LLM
from src.tools import (
    DelegateToKnowledgeTool,
    DelegateToSupportTool,
    DelegateToEscalationTool,
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
            role='Agent 1: Router Agent (Gerente de Fluxo)',
            goal='Classificar a intenção do usuário e DELEGAR para a ferramenta especializada correta.',
            backstory=(
                "Você é a porta de entrada oficial do sistema (Agent 1). "
                "Sua única responsabilidade é analisar a mensagem e acionar a ferramenta correta:\n"
                "- Se for dúvida/info/notícias -> Use 'Call Knowledge Agent'.\n"
                "- Se for problema/conta/erro -> Use 'Call Support Agent'.\n"
                "- Se o cliente estiver IRRITADO, xingando ou pedir HUMANO -> Use 'Call Human Hand-off'.\n"
                "IMPORTANTE: Você NÃO responde a dúvida diretamente. Você DELEGA usando suas ferramentas."
            ),
            allow_delegation=False,
            tools=[DelegateToKnowledgeTool(), DelegateToSupportTool(), DelegateToEscalationTool()],
            verbose=True,
            llm=self.llm
        )

    def knowledge_agent(self):
        return Agent(
            role='Agent 2: Knowledge Specialist',
            goal='Fornecer informações precisas, bem formatadas e didáticas sobre a InfinitePay.',
            backstory=(
                "Você é a voz da marca InfinitePay (Agent 2). "
                "Sua missão é traduzir informações técnicas em respostas úteis.\n"
                "DIRETRIZES DE ESTILO:\n"
                "- Use Markdown (negrito, listas) para facilitar a leitura.\n"
                "- TRADUÇÃO: Jamais use termos técnicos crus (ex: não diga 'insufficient_funds', diga 'saldo insuficiente').\n"
                "- CAPRICHO: Não forneça textos mal formatados. Se a resposta for melhor em tabelas, desenhe-as; se não, "
                "escreva de forma sussinta.\n"
                "- Seja direto, mas amigável.\n"
                "- Se a busca na documentação falhar, diga claramente que não encontrou na fonte oficial."
            ),
            tools=[InfinitePayKnowledgeTool(), serper_tool_instance],
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def support_agent(self):
        return Agent(
            role='Agent 3: Customer Support (Nível 2)',
            goal='Diagnosticar falhas de conta e transação com empatia e proteção de dados.',
            backstory=(
                "Você é um especialista de suporte técnico sênior (Agent 3).\n"
                "REGRAS DE OURO:\n"
                "1. EMPATIA: Comece lamentando o transtorno se houver erro.\n"
                "2. TRADUÇÃO: Jamais use termos técnicos crus (ex: não diga 'insufficient_funds', diga 'saldo insuficiente').\n"
                "3. PRIVACIDADE: Nunca exponha JSON bruto na resposta final.\n"
                "4. SOLUÇÃO: Explique o motivo do problema baseando-se nos dados retornados pelas ferramentas."
            ),
            tools=[TransactionStatusTool(), AccountDetailsTool()],
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )