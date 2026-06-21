import requests
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def ask_llm(user_message):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "qwen/qwen3-coder:free",
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    data = response.json()

    return data["choices"][0]["message"]["content"]