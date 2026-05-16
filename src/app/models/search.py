from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from src.app.models.base import Base


class SearchRun(Base):
    __tablename__ = "search_runs"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(String(64), unique=True, index=True, nullable=False)
    query = Column(String(500), nullable=False)
    inventories = Column(JSON, nullable=False, default=list)
    request_payload = Column(JSON, nullable=False, default=dict)
    warnings = Column(JSON, nullable=False, default=list)
    result_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    provider_runs = relationship(
        "ProviderRun", back_populates="search_run", cascade="all, delete-orphan"
    )


class ProviderRun(Base):
    __tablename__ = "provider_runs"

    id = Column(Integer, primary_key=True, index=True)
    search_run_id = Column(Integer, ForeignKey("search_runs.id", ondelete="CASCADE"))
    provider = Column(String(100), nullable=False)
    inventory_type = Column(String(32), nullable=False)
    configured = Column(Boolean, nullable=False, default=False)
    success = Column(Boolean, nullable=False, default=False)
    cache_hit = Column(Boolean, nullable=False, default=False)
    result_count = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Integer, nullable=False, default=0)
    error_message = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    search_run = relationship("SearchRun", back_populates="provider_runs")
