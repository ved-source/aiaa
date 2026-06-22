import requests
from config import OPENROUTER_API_KEY


def get_embedding(text: str):

    text = text.replace("\n", " ")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/text-embedding-3-small",
        "input": text,
        "dimensions": 1024
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    res_json = response.json()

    embedding = res_json["data"][0]["embedding"]

    return embedding