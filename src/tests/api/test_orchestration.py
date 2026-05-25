from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from src.app.schemas.search import (
    ClarificationBudgetRange,
    ClarificationState,
    DegradedProvider,
    DegradedState,
    FlightFilters,
    InventoryType,
    ProviderStatus,
    SearchDateRange,
    SearchRequest,
    SearchResponse,
    StayFilters,
    TravelerCounts,
)

client = TestClient(app)

_SEARCH_PAYLOAD = {
    "query": "beach vacation",
    "inventory": ["flight"],
    "origin": "DEN",
    "date_range": {"start": "2026-09-01", "end": "2026-09-08"},
    "travelers": {"adults": 2, "children": 0, "infants": 0},
    "stay_filters": {"amenities": []},
    "flight_filters": {"nonstop": False},
    "currency_code": "USD",
    "limit_per_provider": 5,
}


def _make_degraded_response(**kwargs) -> dict:
    base = {
        "search_id": "sid-1",
        "query": "beach vacation",
        "requested_inventory": ["flight"],
        "applied_filters": {
            "travelers": {"adults": 2, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
        },
        "provider_status": [
            {
                "provider": "duffel",
                "label": "Duffel",
                "configured": True,
                "healthy": False,
                "inventory_types": ["flight"],
                "reason": "connection timeout",
            }
        ],
        "degraded_state": {
            "active": True,
            "inventory_types": ["flight"],
            "degraded_providers": [
                {
                    "provider": "duffel",
                    "label": "Duffel",
                    "reason": "connection timeout",
                    "inventory_types": ["flight"],
                }
            ],
        },
        "warnings": ["Duffel unavailable — flight prices may not reflect live rates."],
        "results": [],
        "clarification_state": None,
    }
    base.update(kwargs)
    return base


# --- RED: degraded metadata passthrough ---


def test_orchestrator_with_search_payload_returns_search_response() -> None:
    """When search_payload is included, orchestrator response includes search_response field."""
    with patch("src.app.api.v1.orchestration._SEARCH_SERVICE") as mock_svc:
        mock_svc.search = AsyncMock(
            return_value=SearchResponse(**_make_degraded_response())
        )
        response = client.post(
            "/api/v1/orchestrator/turn",
            json={
                "session_id": "test-search-passthrough",
                "message": "beach vacation",
                "search_payload": _SEARCH_PAYLOAD,
            },
        )
    assert response.status_code == 200
    payload = response.json()
    assert "search_response" in payload, "search_response must be present when search_payload provided"
    assert payload["search_response"] is not None


def test_orchestrator_exposes_degraded_state_in_search_response() -> None:
    """degraded_state from SearchResponse is surfaced through the orchestrator turn response."""
    with patch("src.app.api.v1.orchestration._SEARCH_SERVICE") as mock_svc:
        mock_svc.search = AsyncMock(
            return_value=SearchResponse(**_make_degraded_response())
        )
        response = client.post(
            "/api/v1/orchestrator/turn",
            json={
                "session_id": "test-degraded-state",
                "message": "beach vacation",
                "search_payload": _SEARCH_PAYLOAD,
            },
        )
    assert response.status_code == 200
    payload = response.json()
    sr = payload.get("search_response") or {}
    assert sr.get("degraded_state", {}).get("active") is True


def test_orchestrator_clarification_state_passes_through_search_response() -> None:
    """clarification_state from SearchResponse is present in search_response for continuity."""
    clarification = {
        "destination": {
            "slot": "destination",
            "confidence": 0.9,
            "ambiguous": False,
            "explicit_unknown": False,
            "source": "extracted",
        },
        "timeline": {
            "slot": "timeline",
            "confidence": 0.9,
            "ambiguous": False,
            "explicit_unknown": False,
            "source": "extracted",
        },
        "trip_length": {
            "slot": "trip_length",
            "confidence": 0.5,
            "ambiguous": False,
            "explicit_unknown": False,
            "source": "system",
        },
        "budget": {
            "slot": "budget",
            "confidence": 0.5,
            "ambiguous": False,
            "explicit_unknown": False,
            "source": "system",
        },
        "recap": {"chips": [], "continue_label": "Continue"},
        "all_critical_slots_resolved": True,
        "flight_requirements_pending": [],
    }
    with patch("src.app.api.v1.orchestration._SEARCH_SERVICE") as mock_svc:
        mock_svc.search = AsyncMock(
            return_value=SearchResponse(
                **_make_degraded_response(clarification_state=clarification)
            )
        )
        response = client.post(
            "/api/v1/orchestrator/turn",
            json={
                "session_id": "test-clarification-passthrough",
                "message": "beach vacation",
                "search_payload": _SEARCH_PAYLOAD,
            },
        )
    assert response.status_code == 200
    payload = response.json()
    sr = payload.get("search_response") or {}
    assert sr.get("clarification_state") is not None


def test_orchestrator_without_search_payload_omits_search_response() -> None:
    """When no search_payload, search_response is absent or null."""
    response = client.post(
        "/api/v1/orchestrator/turn",
        json={"session_id": "test-no-payload", "message": "I want a beach vacation."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("search_response") is None


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
