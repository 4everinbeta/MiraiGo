from src.app.db.redis import check_redis_connection, get_redis_client
from src.app.db.session import SessionLocal, check_database_connection


def test_db_session_creation():
    session = SessionLocal()
    assert session is not None
    session.close()


def test_database_connection_check():
    assert check_database_connection() is True


def test_redis_client_creation():
    client = get_redis_client()
    assert client is not None


def test_redis_connection_check(monkeypatch):
    monkeypatch.setattr("src.app.db.redis.redis_client.ping", lambda: True)
    assert check_redis_connection() is True
