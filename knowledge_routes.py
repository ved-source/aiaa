from flask import session, render_template, redirect
from config import supabase
from pinecone_utils import delete_pdf_vectors


def knowledge_page():

    if "user_id" not in session:
        return redirect("/login")

    tenant_id = session["tenant_id"]

    docs = (
        supabase.table("tenant_documents")
        .select("*")
        .eq("tenant_id", tenant_id)
        .order("uploaded_at", desc=True)
        .execute()
    )

    return render_template(
        "knowledge.html",
        documents=docs.data
    )


def delete_document(document_id):

    if "user_id" not in session:
        return redirect("/login")

    tenant_id = session["tenant_id"]

    result = (
        supabase.table("tenant_documents")
        .select("*")
        .eq("id", document_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if len(result.data) == 0:
        return redirect("/knowledge")

    doc = result.data[0]
    filename = doc["original_filename"]

    try:
        # Delete matching vectors in Pinecone by metadata filter source=filename
        delete_pdf_vectors(tenant_id, filename)

        # Delete document record in Supabase
        supabase.table("tenant_documents").delete().eq("id", document_id).execute()

    except Exception as e:
        print("Delete error:", e)

    return redirect("/knowledge")