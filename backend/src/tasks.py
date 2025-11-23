from crewai import Task

class InfinitePayTasks:
    
    def handle_user_request_task(self, agent):
        return Task(
            description=(
                "O usuário enviou a seguinte mensagem: '{query}'\n"
                "ID do Usuário (se disponível/identificado): '{user_id}'\n\n"
                "Sua missão:\n"
                "1. Responda exatamente na mesma linguagem que em '{query}\n"
                "2. Analise a mensagem para entender se é uma Dúvida Geral ou Suporte de Conta.\n"
                "3. Escolha a ferramenta adequada para buscar a informação.\n"
                "4. Se precisar do user_id para a ferramenta e ele não estiver na mensagem, peça ao usuário.\n"
                "5. Com a informação retornada pela ferramenta, elabore a resposta final.\n"
                
            ),
            agent=agent,
            expected_output="Uma resposta útil, correta e baseada nas informações extraídas das ferramentas.",
        )