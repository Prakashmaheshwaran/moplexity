from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    selected_model_id = Column(Integer, ForeignKey("llm_models.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    selected_model = relationship("LLMModel", back_populates="conversations")

