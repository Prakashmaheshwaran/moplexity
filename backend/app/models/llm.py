from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.base import Base


class LLMModel(Base):
    __tablename__ = "llm_models"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(200), nullable=False, unique=True)  # e.g., 'gemini/gemini-2.0-pro', 'ollama/llama2'
    api_key = Column(Text, nullable=False)  # API key for the model
    base_url = Column(String(500), nullable=True)  # Optional base URL for custom endpoints (e.g., Ollama)
    provider_type = Column(String(50), nullable=True)  # Optional provider type (inferred from model_name if not provided)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    conversations = relationship("Conversation", back_populates="selected_model")

