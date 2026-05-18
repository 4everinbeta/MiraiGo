from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_degraded_without_dependencies(monkeypatch):
    async def fake_provider_status():
        return []

    monkeypatch.setattr("src.app.main.check_database_connection", lambda: False)
    monkeypatch.setattr("src.app.main.check_redis_connection", lambda: False)
    monkeypatch.setattr("src.app.main.search_service.provider_status", fake_provider_status)

    response = client.get("/health/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["warnings"]
