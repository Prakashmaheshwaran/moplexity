from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.base import Base


class SearchCache(Base):
    __tablename__ = "search_cache"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(500), nullable=False, index=True)
    results_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

