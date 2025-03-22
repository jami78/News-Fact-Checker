import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory
from app.utils.helpers import BASE_DIR

def get_pdf_file(db: Session, username: str):
    """ Retrieves the latest fact-checking PDF file URL for the user. """
    pdf_file = db.query(ChatHistory.pdf_file_url).filter(ChatHistory.username == username).order_by(ChatHistory.timestamp.desc()).first()

    if not pdf_file or pdf_file[0] is None:
        raise HTTPException(status_code=404, detail="PDF File not found")

    absolute_path = os.path.join(BASE_DIR, pdf_file[0])

    if not os.path.exists(absolute_path):
        raise HTTPException(status_code=404, detail=f"File does not exist at: {absolute_path}")

    return absolute_path

def get_google_doc_url(db: Session, username: str):
    """ Retrieves the latest Google Docs URL for the user. """
    google_doc_url = db.query(ChatHistory.google_doc_url).filter(ChatHistory.username == username).order_by(ChatHistory.timestamp.desc()).first()

    if not google_doc_url or google_doc_url[0] is None:
        raise HTTPException(status_code=404, detail="Google Doc URL not found")

    return google_doc_url[0]
