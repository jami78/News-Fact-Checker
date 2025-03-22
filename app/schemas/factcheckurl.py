from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any

class FactCheckURLs(BaseModel):
    claim: str
    urls: List[HttpUrl]