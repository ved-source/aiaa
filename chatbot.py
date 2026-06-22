import os
import requests
from memory import get_chat_history

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def ask_llm(message, tenant_id, user_id):

    history = get_chat_history(
        tenant_id,
        user_id
    )

    messages = []

    # previous history
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # current user message
    messages.append({
        "role": "user",
        "content": message
    })

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aiaa.up.railway.app",
        "X-Title": "AIAA"
    }

    payload = {
        "model": "openrouter/auto",
        "messages": messages
    }

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        data = response.json()

        print("OPENROUTER RESPONSE:", data)

        if "error" in data:
            return f"OpenRouter Error: {data['error']['message']}"

        if "choices" not in data:
            return f"Unexpected response: {data}"

        reply = data["choices"][0]["message"]["content"]

        return reply

    except Exception as e:
        return f"Error: {str(e)}"