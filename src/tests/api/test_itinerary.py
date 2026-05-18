from fastapi.testclient import TestClient

from src.app.main import app
from src.app.providers.base import ProviderError, TravelProvider
from src.app.schemas.search import FlightSearchResult, InventoryType, SearchRequest

client = TestClient(app)


class MockFlightProvider(TravelProvider):
    provider_name = "mock-flight"
    display_name = "Mock Flight"
    inventory_types = (InventoryType.FLIGHT,)

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        return [
            FlightSearchResult(
                inventory_type=InventoryType.FLIGHT,
                provider=self.provider_name,
                provider_label=self.display_name,
                title="SEA to YVR",
                description="Direct flight",
                total_price=420,
                currency="USD",
                score=80,
                origin_code="SEA",
                destination_code="YVR",
                departure_at="2026-07-01T09:00:00",
                arrival_at="2026-07-01T10:00:00",
                carrier_codes=["AS"],
                stops=0,
            )
        ]


class MockFailingStayProvider(TravelProvider):
    provider_name = "mock-stay"
    display_name = "Mock Stay"
    inventory_types = (InventoryType.STAY,)

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        raise ProviderError("mock stay provider unavailable")


class MockUnconfiguredProvider(TravelProvider):
    provider_name = "mock-offline"
    display_name = "Mock Offline"
    inventory_types = (InventoryType.FLIGHT,)

    @property
    def is_configured(self) -> bool:
        return False

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        return []


def _proposal_snapshot():
    return {
        "proposal_id": "proposal-1",
        "destination": "Vancouver Island",
        "destination_region_key": "vancouver-island",
        "travel_window": {"start": "2026-07-01", "end": "2026-07-07"},
        "duration_nights": 6,
        "travelers": {"adults": 2, "children": 1, "infants": 0},
        "needs_car": True,
        "cost_estimate": {
            "total_estimated": 6400,
            "flight_estimated": 2100,
            "stay_estimated": 3400,
            "car_estimated": 900,
            "currency_code": "USD",
            "confidence": "medium",
        },
        "rationale": "Nature-focused summer itinerary",
        "within_budget": True,
        "over_budget_note": None,
    }


def test_itinerary_propose_endpoint_returns_proposals(fake_redis):
    response = client.post(
        "/api/v1/itinerary/propose",
        json={
            "query": "Plan a family of three nature trip this summer with a budget of $6000-$7500",
            "candidate_destinations": [
                "Vancouver Island",
                "New England",
                "Pacific Northwest",
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["proposals"], list)
    assert len(payload["proposals"]) >= 1


def test_itinerary_price_endpoint_returns_flight_results(monkeypatch, fake_redis):
    monkeypatch.setattr(
        "src.app.services.itinerary.get_provider_registry",
        lambda: [MockFlightProvider(), MockFailingStayProvider()],
    )

    response = client.post(
        "/api/v1/itinerary/price",
        json={
            "proposal_id": "proposal-1",
            "proposal_snapshot": _proposal_snapshot(),
            "travelers": {"adults": 2, "children": 0, "infants": 0},
            "currency_code": "USD",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["flight_results"]) >= 1
    assert any(status["provider"] == "mock-flight" for status in payload["provider_status"])


def test_itinerary_price_endpoint_handles_unavailable_providers(monkeypatch, fake_redis):
    monkeypatch.setattr(
        "src.app.services.itinerary.get_provider_registry",
        lambda: [MockUnconfiguredProvider()],
    )

    response = client.post(
        "/api/v1/itinerary/price",
        json={
            "proposal_id": "proposal-1",
            "proposal_snapshot": _proposal_snapshot(),
            "travelers": {"adults": 2, "children": 0, "infants": 0},
            "currency_code": "USD",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["flight_results"] == []
    assert payload["stay_results"] == []
    assert len(payload["provider_status"]) >= 1
