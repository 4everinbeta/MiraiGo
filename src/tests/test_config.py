from src.app.core.config import settings


def test_settings_loading():
    assert settings.PROJECT_NAME == "MiraiGo"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.SEARCH_CACHE_TTL_SECONDS == 900
    assert settings.DUFFEL_API_URL == "https://api.duffel.com"
