from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any

class ChatHistoryResponse(BaseModel):
    chat_history: List[Dict[str, Any]]
