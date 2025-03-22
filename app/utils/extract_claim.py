import os
from langchain.document_loaders import UnstructuredURLLoader, PyMuPDFLoader
from fastapi import UploadFile
from app.utils.helpers import get_user_folder

async def extract_claim_text(claim: str, url: str, pdf_file: UploadFile, current_user: str) -> str:
    """Extracts claim text from direct input, URL, or PDF file."""

    # Use direct claim if available
    if claim:
        return claim

    # Load claim from URL
    if url:
        loader = UnstructuredURLLoader(urls=[str(url)]) 
        documents = loader.load()
        return "\n".join([doc.page_content for doc in documents])

    # Extract claim from PDF
    if pdf_file:
        user_folder = get_user_folder(current_user)
        pdf_path = os.path.join(user_folder, pdf_file.filename)

        with open(pdf_path, "wb") as buffer:
            buffer.write(await pdf_file.read())

        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        return "\n".join([doc.page_content for doc in documents])


    return ""
