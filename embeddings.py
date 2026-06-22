from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def get_embedding(text: str):

    text = text.replace("\n", " ")

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()