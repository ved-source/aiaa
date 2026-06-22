from config import index
from embeddings import get_embedding
import uuid


def upsert_chunks(
        chunks,
        tenant_id,
        filename
):

    vectors = []

    for i, chunk in enumerate(chunks):

        embedding = get_embedding(chunk)

        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": filename,
                "chunk_id": i
            }
        })

    index.upsert(
        vectors=vectors,
        namespace=tenant_id
    )


def retrieve_chunks(
        query_embedding,
        tenant_id,
        top_k=5
):

    result = index.query(
        namespace=tenant_id,
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    context = []

    for match in result["matches"]:
        context.append(
            match["metadata"]["text"]
        )

    return "\n\n".join(context)


def delete_pdf_vectors(
        tenant_id,
        filename
):

    index.delete(
        namespace=tenant_id,
        filter={
            "source": filename
        }
    )


def retrieve_context(
        query,
        tenant_id,
        top_k=5
):

    query_embedding = get_embedding(query)

    result = index.query(
        namespace=tenant_id,
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    context = []

    for match in result.get("matches", []):
        context.append(
            match["metadata"]["text"]
        )

    return context