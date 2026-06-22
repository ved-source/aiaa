from flask import Blueprint, request, redirect, render_template, session
from supabase import create_client
from pdf_processor import process_pdf
from pinecone_utils import upsert_chunks, delete_pdf_vectors
import os

upload_bp = Blueprint("upload", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)


@upload_bp.route("/upload", methods=["GET", "POST"])
def upload():

    if "user_id" not in session:
        return redirect("/login")

    tenant_id = session["tenant_id"]

    if request.method == "POST":

        file = request.files["pdf"]

        if file.filename == "":
            return redirect("/upload")

        os.makedirs("uploads", exist_ok=True)

        filepath = os.path.join(
            "uploads",
            file.filename
        )

        file.save(filepath)

        chunks = process_pdf(filepath)

        upsert_chunks(
            chunks=chunks,
            tenant_id=tenant_id,
            filename=file.filename
        )

        supabase.table("pdf_documents").insert({
            "tenant_id": tenant_id,
            "filename": file.filename,
            "chunk_count": len(chunks)
        }).execute()

        return redirect("/knowledge")

    return render_template("upload.html")


@upload_bp.route("/knowledge")
def knowledge():

    tenant_id = session["tenant_id"]

    docs = (
        supabase.table("pdf_documents")
        .select("*")
        .eq("tenant_id", tenant_id)
        .execute()
    )

    return render_template(
        "knowledge.html",
        documents=docs.data
    )


@upload_bp.route("/delete_pdf/<filename>")
def delete_pdf(filename):

    tenant_id = session["tenant_id"]

    delete_pdf_vectors(
        tenant_id,
        filename
    )

    (
        supabase.table("pdf_documents")
        .delete()
        .eq("tenant_id", tenant_id)
        .eq("filename", filename)
        .execute()
    )

    return redirect("/knowledge")