from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.base import Base


class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"))
    title = Column(String(500), nullable=False)
    url = Column(Text, nullable=False)
    snippet = Column(Text)
    source_type = Column(String(50), nullable=False)  # 'web', 'social', 'academic'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    message = relationship("Message", back_populates="sources")

