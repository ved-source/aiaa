import os
import requests

from memory import get_chat_history
from pinecone_utils import retrieve_context

from config import OPENROUTER_API_KEY


SYSTEM_PROMPT = """
You are an AI assistant for an ecommerce business.

Rules:

1. Use retrieved knowledge whenever relevant.
2. Never hallucinate information.
3. If the answer is unavailable in uploaded documents, answer normally.
4. Maintain conversation continuity.
5. Never mention Pinecone, vectors, embeddings, or internal architecture.
6. Never mix information across tenants.
7. Be concise and helpful.
"""


def rag_chat(
        question,
        tenant_id,
        user_id
):

    history = get_chat_history(
        tenant_id,
        user_id
    )

    contexts = retrieve_context(
        question,
        tenant_id
    )

    context_text = "\n\n".join(contexts)

    messages = []

    messages.append(
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    )

    if len(context_text) > 0:

        messages.append(
            {
                "role": "system",
                "content":
f"""
Relevant knowledge:

{context_text}
"""
            }
        )

    for msg in history[-20:]:

        messages.append(
            {
                "role": msg["role"],
                "content": msg["content"]
            }
        )

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    headers = {

        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            "https://aiaa.up.railway.app",

        "X-Title":
            "AIAA"
    }

    payload = {

        "model":
            "openrouter/auto",

        "models": [

            "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",

            "deepseek/deepseek-r1-0528:free",

            "qwen/qwen3-coder:free"

        ],

        "messages": messages

    }

    try:

        response = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers=headers,

            json=payload,

            timeout=120

        )

        data = response.json()

        if "error" in data:

            return (
                "OpenRouter Error : "
                + data["error"]["message"]
            )

        answer = data["choices"][0]["message"]["content"]

        return answer

    except Exception as e:

        return str(e)