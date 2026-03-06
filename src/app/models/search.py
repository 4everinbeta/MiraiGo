from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.app.models.base import Base
from src.app.core.security import encrypt_data, decrypt_data

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    query = Column(String)
    # Encrypted results or metadata
    encrypted_results = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="search_histories")

class UserPreference(Base):
    __tablename__ = "user_preference"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True)
    # Encrypted preferences JSON
    encrypted_prefs = Column(String)
    
    user = relationship("User", back_populates="preference")
