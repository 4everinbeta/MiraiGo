from unittest.mock import patch, MagicMock
from src.app.db.session import SessionLocal
from src.app.db.redis import get_redis_client

def test_db_session_creation():
    with patch("src.app.db.session.sessionmaker") as mock_sessionmaker:
        mock_sessionmaker.return_value = MagicMock()
        session = SessionLocal()
        assert session is not None

def test_redis_client_creation():
    with patch("redis.Redis") as mock_redis:
        mock_redis.return_value = MagicMock()
        client = get_redis_client()
        assert client is not None
