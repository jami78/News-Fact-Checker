from fastapi import APIRouter, Depends
from app.schemas.chathistory import ChatHistoryResponse
from app.core.database import get_db
from app.auth.auth import get_current_user
from app.db.crud.chat_history import get_chat_history
from sqlalchemy.orm import Session
router = APIRouter()

@router.get("/chat-history/", response_model=ChatHistoryResponse)
async def fetch_chat_history(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """ Retrieves user chat history. """
    history = get_chat_history(db, current_user)
    return {"chat_history": history}