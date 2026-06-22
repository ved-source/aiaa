from pypdf import PdfReader
from pinecone_utils import upsert_chunks


def extract_text(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def chunk_text(text, size=500, overlap=80):

    words = text.split()

    chunks = []
    i = 0

    while i < len(words):

        chunk = " ".join(words[i:i + size])

        if chunk.strip():
            chunks.append(chunk.strip())

        i += size - overlap

    return chunks


def process_pdf(
        pdf_path,
        tenant_id,
        file_name
):

    text = extract_text(pdf_path)

    chunks = chunk_text(text)

    upsert_chunks(
        chunks,
        tenant_id,
        file_name
    )

    return len(chunks)