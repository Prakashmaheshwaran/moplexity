from pydantic import BaseModel
from typing import List
from datetime import datetime
from .source import Source


class MessageBase(BaseModel):
    role: str
    content: str


class MessageCreate(MessageBase):
    conversation_id: int


class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
    sources: List[Source] = []
    
    class Config:
        from_attributes = True

