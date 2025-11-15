from pydantic import BaseModel, Field
from typing import List, Optional
from .source import Source


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[int] = None
    model_id: Optional[int] = None
    pro_mode: bool = False
    focus_mode: str = 'web'  # 'web', 'social', 'academic'
    focus_modes: Optional[List[str]] = None


class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    content: str
    sources: List[Source] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)

