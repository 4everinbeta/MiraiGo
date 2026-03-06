from unittest.mock import MagicMock
from src.app.models.user import User
# Need to import these so SQLAlchemy knows about them for relationships
from src.app.models.search import SearchHistory, UserPreference

def test_user_model_creation():
    user = User(
        full_name="Test User",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )
    assert user.full_name == "Test User"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password"
    assert user.is_active is True
    assert user.is_superuser is False
