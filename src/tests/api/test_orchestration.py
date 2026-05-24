from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_orchestrator_turn_returns_partial_questions() -> None:
    response = client.post(
        "/api/v1/orchestrator/turn",
        json={"session_id": "test-q", "message": "I want a beach vacation."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["response_type"] == "questions"
    assert len(payload["open_questions"]) >= 1
    assert any("subject to change" in text.lower() for text in payload["disclaimers"])


def test_orchestrator_turn_persists_session_state() -> None:
    first = client.post(
        "/api/v1/orchestrator/turn",
        json={
            "session_id": "test-persist",
            "message": "Plan a 5 day trip from Denver for 2 adults with budget 4500 between 2026-08-10 and 2026-08-16",
        },
    )
    assert first.status_code == 200

    second = client.post(
        "/api/v1/orchestrator/turn",
        json={"session_id": "test-persist", "message": "Continue with options"},
    )
    assert second.status_code == 200
    payload = second.json()
    assert payload["response_type"] in {"ideas", "packages", "itineraries"}
    assert payload["session_id"] == "test-persist"
