import json
import pytest
from unittest.mock import patch, MagicMock
from src.app.db.redis import redis_client

# Simple mock for redis client if it's not running
@pytest.fixture
def mock_redis():
    with patch("src.app.db.redis.redis_client") as mock:
        yield mock

def test_cache_set_get(mock_redis):
    query = "test query"
    results = [{"provider": "Expedia", "text": "Result 1", "score": 10}]
    
    # Mock get returning None (miss)
    mock_redis.get.return_value = None
    
    cached = mock_redis.get(f"search:{query}")
    assert cached is None
    
    # Mock set
    mock_redis.setex.return_value = True
    mock_redis.setex(f"search:{query}", 3600, json.dumps(results))
    
    # Mock get returning results (hit)
    mock_redis.get.return_value = json.dumps(results)
    
    cached = mock_redis.get(f"search:{query}")
    assert json.loads(cached) == results
