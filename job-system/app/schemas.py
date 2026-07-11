from pydantic import BaseModel
from typing import Dict, Any, Optional


class JobRequest(BaseModel):
    user_id:str
    payload: Dict[str,Any]
    idempotent_key: str


class EmailPayload(BaseModel):
    to:str
    subject: str

