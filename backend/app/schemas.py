from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Source Schemas
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


# Message Schemas
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


# Conversation Schemas
class ConversationBase(BaseModel):
    title: str
    selected_model_id: Optional[int] = None


class ConversationCreate(ConversationBase):
    pass


class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    selected_model: Optional["LLMModelResponse"] = None

    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    id: int
    title: str
    selected_model_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    selected_model: Optional["LLMModelResponse"] = None

    class Config:
        from_attributes = True


# Chat Schemas
class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[int] = None
    model_id: Optional[int] = None
    pro_mode: bool = False
    focus_mode: str = 'web'  # 'web', 'social', 'academic'


class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    content: str
    sources: List[Source] = []
    follow_up_questions: List[str] = []


# Search Schemas
class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source_type: str


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int


# LLM Provider Schemas
class LLMProviderBase(BaseModel):
    name: str
    provider_type: str
    api_key: str
    is_active: bool = True


class LLMProviderCreate(LLMProviderBase):
    pass


class LLMProviderUpdate(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None


class LLMProviderResponse(LLMProviderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# LLM Model Schemas
class LLMModelBase(BaseModel):
    provider_id: int
    model_name: str
    display_name: str
    description: Optional[str] = None
    is_active: bool = True


class LLMModelCreate(LLMModelBase):
    pass


class LLMModelUpdate(BaseModel):
    provider_id: Optional[int] = None
    model_name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class LLMModelResponse(LLMModelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    provider_name: Optional[str] = None
    provider_type: Optional[str] = None

    class Config:
        from_attributes = True


class LLMModelActiveResponse(BaseModel):
    id: int
    model_name: str
    display_name: str
    description: Optional[str] = None
    provider_name: str
    provider_type: str

    class Config:
        from_attributes = True

