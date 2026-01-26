def build_chat_prompt(history, context, user_message, strict=True):
    """
    Build the prompt for the LLM using:
    - ROLE prompting
    - INSTRUCTION prompting
    - FEW-SHOT prompting (1 short example)
    - CHAT HISTORY
    - RETRIEVED CONTEXT
    """

    # 1) Role Prompting (persona)
    role = "You are a helpful AI assistant. Explain simply and clearly.\n"

    # 2) Instruction Prompting (rules)
    if strict:
        rules = (
            "Use ONLY the retrieved context to answer.\n"
            "If the context is not enough, say: I don't know.\n"
        )
    else:
        rules = "Use the context if useful, but you may use general knowledge.\n"

    # 3) Few-shot prompting (one tiny example)
    example = (
        "Example:\n"
        "Context: RAG = Retrieval-Augmented Generation.\n"
        "User: What is RAG?\n"
        "Assistant: RAG retrieves relevant text first, then generates an answer based on it.\n\n"
    )

    # 4) History text
    history_text = ""
    for msg in history:
        history_text += f"{msg['role']}: {msg['content']}\n"

    # 5) Final prompt
    prompt = (
        role
        + rules
        + "\n"
        + example
        + "Chat History:\n"
        + history_text
        + "\nRetrieved Context:\n"
        + (context if context else "No context found.")
        + "\n\nUser: "
        + user_message
        + "\nAssistant:"
    )

    return prompt
