import json
from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory
from datetime import datetime

def store_fact_check_data(db: Session, session_id: str, username: str, user_query: str, formatted_report: dict, google_doc_url: str, pdf_file_url: str, creative_docx_filename: str):
    """ Stores AI fact-checking responses in the database. """
    fact_check_entry = ChatHistory(
        session_id=session_id,
        username=username,
        user_input=user_query,
        ai_response=json.dumps(formatted_report),
        google_doc_url=google_doc_url,
        pdf_file_url=pdf_file_url,
        creative_docx_file=creative_docx_filename,
        timestamp=datetime.now()
    )
    db.add(fact_check_entry)
    db.commit()
    return fact_check_entry
