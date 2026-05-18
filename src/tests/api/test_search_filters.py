from fastapi.testclient import TestClient

from src.app.main import app
from src.app.providers.base import ProviderError, TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest, StaySearchResult
from src.app.services.search import search_service

client = TestClient(app)


class MixedProvider(TravelProvider):
    provider_name = "mixed"
    display_name = "Mixed Provider"
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
                title="Filtered Stay",
                description="Amenity match",
                total_price=500,
                currency="USD",
                redirect_url="https://example.com/stay",
                deep_link_label="Continue search",
                score=61,
                location_label="Paris",
                amenities=["wifi", "pool"],
                nightly_price=125,
                check_in=None,
                check_out=None,
            )
        ]


class FailingProvider(TravelProvider):
    provider_name = "failing"
    display_name = "Failing Provider"
    inventory_types = (InventoryType.STAY,)

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        raise ProviderError("timeout")


def test_get_search_compat_uses_query_params(fake_redis):
    search_service.providers = [MixedProvider()]

    response = client.get(
        "/api/v1/search",
        params={
            "q": "Paris stay",
            "destination": "Paris",
            "inventory": "stay",
            "max_price": "700",
            "amenities": "wifi",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["applied_filters"]["destination"] == "Paris"
    assert payload["results"][0]["title"] == "Filtered Stay"


def test_search_returns_partial_results_when_one_provider_fails(fake_redis):
    search_service.providers = [MixedProvider(), FailingProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Paris stay",
            "destination": "Paris",
            "inventory": ["stay"],
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["results"]) == 1
    assert any("timeout" in warning for warning in payload["warnings"])
