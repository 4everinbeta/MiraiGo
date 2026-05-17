from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
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


class SearchRun(Base):
    __tablename__ = "search_run"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(String, unique=True, nullable=False, index=True)
    query = Column(String, nullable=False, default="")
    inventories = Column(JSON, nullable=False, default=list)
    request_payload = Column(JSON, nullable=False, default=dict)
    warnings = Column(JSON, nullable=False, default=list)
    result_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    provider_runs = relationship(
        "ProviderRun",
        back_populates="search_run",
        cascade="all, delete-orphan",
    )


class ProviderRun(Base):
    __tablename__ = "provider_run"

    id = Column(Integer, primary_key=True, index=True)
    search_run_id = Column(Integer, ForeignKey("search_run.id"), nullable=False, index=True)
    provider = Column(String, nullable=False, index=True)
    inventory_type = Column(String, nullable=False)
    configured = Column(Boolean, nullable=False, default=False)
    success = Column(Boolean, nullable=False, default=False)
    cache_hit = Column(Boolean, nullable=False, default=False)
    result_count = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Integer, nullable=False, default=0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    search_run = relationship("SearchRun", back_populates="provider_runs")
