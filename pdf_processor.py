from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from pinecone_utils import upsert_chunks


def extract_text(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def chunk_text(text):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,
        chunk_overlap=80,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    return splitter.split_text(text)


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