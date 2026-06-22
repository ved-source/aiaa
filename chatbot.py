from rag_chatbot import rag_chat


def ask_llm(
        question,
        tenant_id,
        user_id
):

    return rag_chat(
        question,
        tenant_id,
        user_id
    )