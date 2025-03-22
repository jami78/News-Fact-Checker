from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory

def get_chat_history(db: Session, username: str):
    """Retrieves user chat history from the database and converts it into a JSON response."""

    history_records = db.query(ChatHistory).filter(ChatHistory.username == username).order_by(ChatHistory.timestamp.desc()).all()

    # ✅ Convert SQLAlchemy objects to dictionaries
    chat_history = []
    for record in history_records:
        chat_history.append({
            "session_id": record.session_id,
            "role": "user",
            "content": record.user_input,
            "timestamp": record.timestamp
        })
        chat_history.append({
            "session_id": record.session_id,
            "role": "assistant",
            "content": record.ai_response,
            "timestamp": record.timestamp
        })

    return chat_history  # ✅ Now returns a valid list of dictionaries
