from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.app.models.base import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    search_id = Column(String(64), index=True, nullable=False)
    query = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    user = relationship("User", back_populates="search_histories")


class UserPreference(Base):
    __tablename__ = "user_preference"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True, nullable=False)
    default_origin = Column(String(100))
    preferred_inventory = Column(JSON, nullable=False, default=list)
    currency = Column(String(3), default="USD")

    user = relationship("User", back_populates="preference")
