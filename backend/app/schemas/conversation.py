from pydantic import BaseModel
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .llm import LLMModelResponse
    from .message import Message
else:
    from .llm import LLMModelResponse
    Message = "Message"


class ConversationBase(BaseModel):
    title: str
    selected_model_id: Optional[int] = None


class ConversationCreate(ConversationBase):
    pass


class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List["Message"] = []
    selected_model: Optional[LLMModelResponse] = None

    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    id: int
    title: str
    selected_model_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    selected_model: Optional[LLMModelResponse] = None

    class Config:
        from_attributes = True

