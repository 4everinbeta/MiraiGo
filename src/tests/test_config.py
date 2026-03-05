from src.app.core.config import settings

def test_settings_loading():
    assert settings.PROJECT_NAME == "MiraiGo"
    assert settings.API_V1_STR == "/api/v1"
