from flask import session, render_template, redirect
from config import supabase
from pinecone_utils import index


def knowledge_page():

    if "user_id" not in session:
        return redirect("/login")

    tenant_id = session["tenant_id"]

    docs = (
        supabase.table("pdf_documents")
        .select("*")
        .eq("tenant_id", tenant_id)
        .order("created_at", desc=True)
        .execute()
    )

    return render_template(
        "knowledge.html",
        docs=docs.data
    )


def delete_document(document_id):

    if "user_id" not in session:
        return redirect("/login")

    tenant_id = session["tenant_id"]

    result = (
        supabase.table("pdf_documents")
        .select("*")
        .eq("id", document_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if len(result.data) == 0:
        return redirect("/knowledge")

    doc = result.data[0]

    filename = doc["filename"]

    try:

        vector_ids = (
            supabase.table("pdf_chunks")
            .select("vector_id")
            .eq("document_id", document_id)
            .execute()
        )

        ids = [v["vector_id"] for v in vector_ids.data]

        if len(ids) > 0:
            index.delete(
                ids=ids,
                namespace=tenant_id
            )

        (
            supabase.table("pdf_chunks")
            .delete()
            .eq("document_id", document_id)
            .execute()
        )

        (
            supabase.table("pdf_documents")
            .delete()
            .eq("id", document_id)
            .execute()
        )

    except Exception as e:
        print(e)

    return redirect("/knowledge")