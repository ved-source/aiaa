import os
from flask import Blueprint, request, redirect, session, render_template
from werkzeug.utils import secure_filename
from supabase import create_client

from pdf_processor import process_pdf

upload_bp = Blueprint(
    "upload_bp",
    __name__
)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)


@upload_bp.route("/upload", methods=["GET", "POST"])
def upload_pdf():

    if "user_id" not in session:
        return redirect("/login")

    tenant_id = session["tenant_id"]

    if request.method == "POST":

        if "pdf" not in request.files:
            return "No file uploaded"

        file = request.files["pdf"]

        if file.filename == "":
            return "No file selected"

        filename = secure_filename(file.filename)

        save_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(save_path)

        chunk_count = process_pdf(
            save_path,
            tenant_id,
            filename
        )

        supabase.table(
            "pdf_files"
        ).insert(
            {
                "tenant_id": tenant_id,
                "file_name": filename,
                "chunk_count": chunk_count
            }
        ).execute()

        return redirect("/upload")

    files = (

        supabase.table(
            "pdf_files"
        )

        .select("*")

        .eq(
            "tenant_id",
            tenant_id
        )

        .order(
            "created_at",
            desc=True
        )

        .execute()

    )

    return render_template(
        "upload.html",
        files=files.data
    )