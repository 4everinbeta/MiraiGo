import pytest

from src.app.schemas.search import InventoryType, SearchDateRange, SearchRequest, TravelerCounts


@pytest.mark.asyncio
async def test_amadeus_provider_builds_flight_results():
    from src.app.providers.amadeus import AmadeusFlightsProvider

    provider = AmadeusFlightsProvider()
    provider.client_id = "client-id"
    provider.client_secret = "client-secret"
    provider.api_url = "https://test.api.amadeus.com"

    async def fake_token(force_refresh: bool = False) -> str:
        return "oauth-token"

    async def fake_offers(token: str, params: dict):
        assert token == "oauth-token"
        return (
            200,
            {
                "data": [
                    {
                        "price": {"total": "640.00", "currency": "USD"},
                        "itineraries": [
                            {
                                "duration": "PT10H45M",
                                "segments": [
                                    {
                                        "carrierCode": "TP",
                                        "departure": {
                                            "iataCode": "DEN",
                                            "at": "2026-05-03T09:30:00",
                                        },
                                        "arrival": {
                                            "iataCode": "BCN",
                                            "at": "2026-05-03T20:15:00",
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                ]
            },
        )

    provider._get_oauth_token = fake_token
    provider._flight_offers_request = fake_offers

    results = await provider.search(
        SearchRequest(
            destination="BCN",
            origin="DEN",
            inventory=[InventoryType.FLIGHT],
            date_range=SearchDateRange(start="2026-05-03", end="2026-05-08"),
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.FLIGHT,
    )

    assert len(results) == 1
    result = results[0]
    assert result.provider == "amadeus"
    assert result.provider_label == "Amadeus"
    assert result.total_price == 640.0
