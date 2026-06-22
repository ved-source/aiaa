from pinecone_utils import retrieve_context
from memory import get_chat_history
from chatbot import ask_llm


def rag_chat(
        message,
        tenant_id,
        user_id
):

    history = get_chat_history(
        tenant_id,
        user_id
    )

    contexts = retrieve_context(
        message,
        tenant_id
    )

    context_text = "\n\n".join(contexts)

    prompt = f"""

Relevant information:

{context_text}


User Question:

{message}

Answer only using the information above if available.
If unavailable, answer normally.
"""

    return ask_llm(
        prompt,
        tenant_id,
        user_id
    )