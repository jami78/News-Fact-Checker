from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any


class FactCheckRequest(BaseModel):
    claim: Optional[str] = None
    url: Optional[HttpUrl] = None



class FactCheckResponse(BaseModel):
    session_id: str
    claim: str
    fact_check_result: str
    urls: List[HttpUrl]