from crewai import Task

class InfinitePayTasks:
    
    def router_task(self, agent, query, user_id):
        
        current_date = "24 de novembro de 2025"

        return Task(
            description=(
                f"Mensagem recebida: '{query}' (User ID: {user_id})\n"
                f"Data atual: {current_date}\n\n"
                "Sua missão é atuar como um ROTEADOR INTELIGENTE.\n"
                "Você deve identificar o tópico e chamar a ferramenta correta.\n\n"
                "REGRA DE DECISÃO:\n"
                "1. CASO KNOWLEDGE (Taxas, Produtos, Dúvidas Gerais):\n"
                "   -> AÇÃO: Execute 'Call Knowledge Agent'.\n\n"
                "2. CASO SUPPORT (Erros, Conta, Transações):\n"
                "   -> AÇÃO: Execute 'Call Support Agent' com input '{user_id}|{query}'.\n\n"
                "3. CASO ESCALATION (Cliente bravo, pede atendente, reclamação grave):\n"
                "   -> AÇÃO: Execute a ferramenta 'Call Human Hand-off'.\n"
                "   -> INPUT: '{user_id}|{query}' (Use a barra vertical).\n\n"
                "IMPORTANTE: Não altere o texto que a ferramenta retornar. "
                "Mantenha a formatação Markdown (Tabelas, Negritos) exatamente como vier."
            ),
            agent=agent,
            expected_output=(
                "O conteúdo exato retornado pela ferramenta, preservando toda a formatação Markdown."
            ),
        )