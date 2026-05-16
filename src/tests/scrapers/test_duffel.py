import pytest

from src.app.providers.base import ProviderError
from src.app.providers.duffel import DuffelFlightsProvider
from src.app.schemas.search import InventoryType, SearchDateRange, SearchRequest, TravelerCounts


@pytest.mark.asyncio
async def test_duffel_provider_builds_flight_results(monkeypatch):
    provider = DuffelFlightsProvider()
    provider.access_token = "test-token"

    async def fake_resolve_place_code(location: str):
        return {"Denver": "DEN", "Barcelona": "BCN"}[location]

    async def fake_create_offer_request(payload: dict):
        assert payload["data"]["slices"][0]["origin"] == "DEN"
        assert payload["data"]["slices"][0]["destination"] == "BCN"
        return {
            "data": {
                "offers": [
                    {
                        "owner": {"name": "Duffel Airways"},
                        "total_amount": "640.00",
                        "total_currency": "USD",
                        "slices": [
                            {
                                "duration": "PT10H45M",
                                "segments": [
                                    {
                                        "departing_at": "2026-05-03T09:30:00",
                                        "arriving_at": "2026-05-03T20:15:00",
                                        "origin": {"iata_code": "DEN"},
                                        "destination": {"iata_code": "BCN"},
                                        "operating_carrier": {
                                            "iata_code": "TP",
                                            "name": "TAP Air Portugal",
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }
        }

    monkeypatch.setattr(provider, "_resolve_place_code", fake_resolve_place_code)
    monkeypatch.setattr(provider, "_create_offer_request", fake_create_offer_request)

    results = await provider.search(
        SearchRequest(
            destination="Barcelona",
            origin="Denver",
            inventory=[InventoryType.FLIGHT],
            date_range=SearchDateRange(start="2026-05-03", end="2026-05-08"),
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.FLIGHT,
    )

    assert len(results) == 1
    result = results[0]
    assert result.provider == "duffel"
    assert result.title == "DEN to BCN roundtrip"
    assert result.total_price == 640.0
    assert result.redirect_url is None


@pytest.mark.asyncio
async def test_duffel_provider_rejects_child_searches():
    provider = DuffelFlightsProvider()
    provider.access_token = "test-token"

    with pytest.raises(ProviderError) as exc_info:
        await provider.search(
            SearchRequest(
                destination="Barcelona",
                origin="Denver",
                inventory=[InventoryType.FLIGHT],
                date_range=SearchDateRange(start="2026-05-03"),
                travelers=TravelerCounts(adults=1, children=1),
            ),
            InventoryType.FLIGHT,
        )

    assert "adults only" in str(exc_info.value)
