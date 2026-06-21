import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def ask_llm(user_message):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aiaa.up.railway.app",
        "X-Title": "AIAA"
    }

    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": "You are AIAA, a helpful AI assistant."
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        data = response.json()

        # Debug output (visible in Railway logs)
        print("OPENROUTER RESPONSE:", data)

        # Error handling
        if "error" in data:
            return f"OpenRouter Error: {data['error'].get('message')}"

        if "choices" not in data:
            return f"Unexpected response:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"