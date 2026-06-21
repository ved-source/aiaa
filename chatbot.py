import requests
import os
from memory import save_message, get_chat_history

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def ask_llm(message, tenant_id, user_id):

    history = get_chat_history(tenant_id, user_id)

    history.append({
        "role": "user",
        "content": message
    })

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
        "models": [
            "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
            "openrouter/auto"
        ],
        "messages": history
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    data = response.json()

    reply = data["choices"][0]["message"]["content"]

    save_message(
        tenant_id,
        user_id,
        "user",
        message
    )

    save_message(
        tenant_id,
        user_id,
        "assistant",
        reply
    )

    return reply