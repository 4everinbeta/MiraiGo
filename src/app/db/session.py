from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.app.core.config import settings

engine = create_engine(settings.get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
