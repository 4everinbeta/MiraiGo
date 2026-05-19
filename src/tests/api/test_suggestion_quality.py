from fastapi.testclient import TestClient

from src.app.main import app
from src.app.providers.base import TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest, StaySearchResult
from src.app.services.search import search_service

client = TestClient(app)


class StayOnlyProvider(TravelProvider):
    provider_name = "staytest"
    display_name = "Stay Test"
    inventory_types = (InventoryType.STAY,)

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        return [
            StaySearchResult(
                inventory_type=InventoryType.STAY,
                provider=self.provider_name,
                provider_label=self.display_name,
                title=f"Stay in {request.destination}",
                description="Test stay result",
                total_price=1100,
                currency="USD",
                score=88,
                location_label=request.destination,
                amenities=["wifi"],
            )
        ]


def test_search_response_contains_labeled_recommendation_packages():
    search_service.providers = [StayOnlyProvider()]
    response = client.post(
        "/api/v1/search",
        json={
            "query": "Lisbon in June for around 2000",
            "destination": "Lisbon",
            "inventory": ["stay"],
            "date_range": {"start": "2026-06-10", "end": "2026-06-16"},
            "budget_range": {"minimum": 1500, "maximum": 2000, "currency_code": "USD"},
            "travelers": {"adults": 2, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["recommendation_packages"]
    package = payload["recommendation_packages"][0]
    assert package["destination"]
    assert package["fallback_level"] in {"high-fit", "partial-fit", "fallback"}
    assert package["rationale_text"]
    assert package["reason_tags"]
    assert package["hard_constraint_status"]["destination"] is True
    assert package["hard_constraint_status"]["timeline"] is True


def test_multi_turn_payload_preserves_resolved_constraints_from_clarification_state():
    search_service.providers = [StayOnlyProvider()]

    first = client.post(
        "/api/v1/search",
        json={
            "query": "Lisbon trip ideas",
            "destination": "Lisbon",
            "inventory": ["stay"],
            "date_range": {"start": "2026-06-10", "end": "2026-06-16"},
            "travelers": {"adults": 2, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )
    assert first.status_code == 200
    first_payload = first.json()

    second = client.post(
        "/api/v1/search",
        json={
            "query": "Lisbon trip ideas",
            "inventory": ["stay"],
            "clarification_state": first_payload["clarification_state"],
            "travelers": {"adults": 2, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["applied_filters"]["destination"] == "Lisbon"
    assert second_payload["applied_filters"]["date_range"] is not None
