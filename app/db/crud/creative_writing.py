import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory
from app.utils.helpers import BASE_DIR


def get_creative_writing_doc(db: Session, username: str):
    """ Retrieves the latest creative writing DOCX file for the user. """
    creative_docx = db.query(ChatHistory.creative_docx_file).filter(ChatHistory.username == username).order_by(ChatHistory.timestamp.desc()).first()

    if not creative_docx or creative_docx[0] is None:
        raise HTTPException(status_code=404, detail="Creative Writing DOCX not found")
    absolute_path = os.path.join(BASE_DIR, creative_docx[0])

    if not os.path.exists(absolute_path):
        raise HTTPException(status_code=404, detail=f"File does not exist at: {absolute_path}")

    return absolute_path
