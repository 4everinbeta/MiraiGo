import pytest

from src.app.providers.base import ProviderError
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


@pytest.mark.asyncio
async def test_amadeus_refreshes_token_once_on_401():
    from src.app.providers.amadeus import AmadeusFlightsProvider

    provider = AmadeusFlightsProvider()
    provider.client_id = "client-id"
    provider.client_secret = "client-secret"
    provider.api_url = "https://test.api.amadeus.com"

    token_calls: list[bool] = []
    request_tokens: list[str] = []

    async def fake_token(force_refresh: bool = False) -> str:
        token_calls.append(force_refresh)
        return "fresh-token" if force_refresh else "cached-token"

    async def fake_offers(token: str, params: dict):
        request_tokens.append(token)
        if len(request_tokens) == 1:
            return 401, {}
        return 200, {"data": []}

    provider._get_oauth_token = fake_token
    provider._flight_offers_request = fake_offers

    result = await provider._search_flight_offers(
        {
            "originLocationCode": "DEN",
            "destinationLocationCode": "BCN",
            "departureDate": "2026-05-03",
            "adults": "1",
            "nonStop": "false",
            "max": "5",
            "currencyCode": "USD",
        }
    )

    assert result == {"data": []}
    assert token_calls == [False, True]
    assert request_tokens == ["cached-token", "fresh-token"]


@pytest.mark.asyncio
async def test_amadeus_raises_after_single_refresh_attempt():
    from src.app.providers.amadeus import AmadeusFlightsProvider

    provider = AmadeusFlightsProvider()
    provider.client_id = "client-id"
    provider.client_secret = "client-secret"
    provider.api_url = "https://test.api.amadeus.com"

    token_calls: list[bool] = []
    request_count = 0

    async def fake_token(force_refresh: bool = False) -> str:
        token_calls.append(force_refresh)
        return f"token-{len(token_calls)}"

    async def always_unauthorized(token: str, params: dict):
        nonlocal request_count
        request_count += 1
        return 401, {}

    provider._get_oauth_token = fake_token
    provider._flight_offers_request = always_unauthorized

    with pytest.raises(ProviderError):
        await provider._search_flight_offers({"originLocationCode": "DEN"})

    assert token_calls == [False, True]
    assert request_count == 2


@pytest.mark.asyncio
async def test_amadeus_healthcheck_reports_unconfigured_when_missing_credentials():
    from src.app.providers.amadeus import AmadeusFlightsProvider

    provider = AmadeusFlightsProvider()
    provider.client_id = None
    provider.client_secret = None

    status = await provider.healthcheck()

    assert status.provider == "amadeus"
    assert status.configured is False
    assert status.healthy is False
