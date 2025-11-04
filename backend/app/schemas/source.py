from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SourceBase(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    source_type: str


class SourceCreate(SourceBase):
    pass


class Source(SourceBase):
    id: int
    message_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

