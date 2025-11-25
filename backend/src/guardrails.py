def input_guardrail(message: str) -> tuple[bool, str]:
    """
    Analisa a mensagem do usuário antes de enviar para os Agentes.
    Retorna: (is_safe: bool, reason: str)
    """
    msg_lower = message.lower()

    competitors = ["stone", "cielo", "pagseguro", "getnet", "safrapay", "moderninha", "picpay", "xp", "master"]
    
    for comp in competitors:
        if comp in msg_lower:
            return False, f"Como assistente da InfinitePay, eu foco apenas em nossos produtos e taxas. Não posso opinar sobre a {comp.capitalize()}."

    unsafe_topics = ["hackear", "fraude", "burlar", "crime", "matar", "roubar senha"]
    
    for topic in unsafe_topics:
        if topic in msg_lower:
            return False, "Sinto muito, mas não posso processar mensagens com conteúdo suspeito ou ilegal."
    return True, ""