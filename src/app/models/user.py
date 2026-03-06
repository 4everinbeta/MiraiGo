from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src.app.models.base import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    
    search_histories = relationship("SearchHistory", back_populates="user")
    preference = relationship("UserPreference", back_populates="user", uselist=False)
