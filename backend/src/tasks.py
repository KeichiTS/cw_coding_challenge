from crewai import Task

class InfinitePayTasks:
    
    def router_task(self, agent, query, user_id):
        return Task(
            description=(
                f"Mensagem recebida: '{query}' (User ID: {user_id})\n\n"
                "Sua missão é acionar o agente correto usando SUAS FERRAMENTAS.\n\n" \
                "Hoje é 24 de novembro de 2025 \n\n"
                "REGRA DE DECISÃO:\n"
                "1. Se o assunto for notícias, futebol, clima, taxas ou produtos:\n"
                "   -> USE A FERRAMENTA: 'Call Knowledge Agent'.\n"
                "   -> Input da ferramenta: A pergunta exata do usuário.\n\n"
                "2. Se o assunto for conta bloqueada, erro, transação ou login:\n"
                "   -> USE A FERRAMENTA: 'Call Support Agent'.\n"
                "   -> Input da ferramenta: '{user_id}|{query}'\n\n"
                "ATENÇÃO: Não tente responder. Não tente delegar nativamente. USE A FERRAMENTA."
            ),
            agent=agent,
            expected_output="A resposta final em texto trazida pela ferramenta.",
        )