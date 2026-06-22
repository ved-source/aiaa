from flask import Blueprint, request, redirect, render_template, session
from config import supabase, PINECONE_INDEX_NAME
from pdf_processor import process_pdf
import os

upload_bp = Blueprint("upload", __name__)


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

        # process_pdf processes, chunks, and upserts to Pinecone, returning chunk count
        chunk_count = process_pdf(
            pdf_path=filepath,
            tenant_id=tenant_id,
            file_name=file.filename
        )

        # Insert document record into tenant_documents in Supabase
        supabase.table("tenant_documents").insert({
            "tenant_id": tenant_id,
            "original_filename": file.filename,
            "storage_path": filepath,
            "pinecone_index_name": PINECONE_INDEX_NAME,
            "pinecone_namespace": tenant_id,
            "chunk_count": chunk_count,
            "status": "processed"
        }).execute()

        return redirect("/knowledge")

    # For GET request, list files under the tenant
    docs = (
        supabase.table("tenant_documents")
        .select("*")
        .eq("tenant_id", tenant_id)
        .order("uploaded_at", desc=True)
        .execute()
    )

    return render_template("upload.html", files=docs.data)