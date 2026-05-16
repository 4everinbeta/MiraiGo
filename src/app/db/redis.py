import redis

from src.app.core.config import settings


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(settings.get_redis_url(), decode_responses=True)


redis_client = get_redis_client()


def check_redis_connection() -> bool:
    try:
        redis_client.ping()
        return True
    except Exception:
        return False
