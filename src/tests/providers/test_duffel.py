from datetime import date
import pytest

from src.app.schemas.search import InventoryType, SearchDateRange, SearchRequest, TravelerCounts
from src.app.services.search import SearchService
from src.app.providers.duffel import DuffelFlightsProvider


def test_duffel_fallback_requests_are_deterministic():
    service = SearchService()
    request = SearchRequest(
        query="Flights to Lisbon",
        destination="Lisbon",
        origin="Denver",
        inventory=[InventoryType.FLIGHT],
        date_range=SearchDateRange(start=date(2026, 6, 10), end=date(2026, 6, 17)),
        flight_filters={"nonstop": True},
    )

    fallbacks = service._duffel_fallback_requests(request)

    assert [label for label, _ in fallbacks] == ["relax_nonstop_filter", "widen_date_window"]
    relaxed_request = fallbacks[0][1]
    widened_request = fallbacks[1][1]
    assert relaxed_request.flight_filters.nonstop is False
    assert widened_request.date_range.start.isoformat() == "2026-06-08"
    assert widened_request.date_range.end.isoformat() == "2026-06-19"


@pytest.mark.asyncio
async def test_duffel_data_mapping_parses_expected_fields(monkeypatch):
    provider = DuffelFlightsProvider()
    provider.access_token = "test-token"

    async def fake_resolve_place_code(location: str):
        return {"Denver": "DEN", "Barcelona": "BCN"}[location]

    async def fake_create_offer_request(payload: dict):
        return {
            "data": {
                "offers": [
                    {
                        "id": "duffel-offer-456",
                        "owner": {"name": "Duffel Airways"},
                        "total_amount": "640.00",
                        "total_currency": "USD",
                        "slices": [
                            {
                                "duration": "PT10H45M",
                                "stops": 0,
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
            date_range=SearchDateRange(start=date(2026, 5, 3), end=date(2026, 5, 8)),
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.FLIGHT,
    )

    assert len(results) == 1
    result = results[0]
    assert result.price_minor == 64000
    assert result.currency_code == "USD"
    assert result.duration_minutes == 645
    assert result.stops_count == 0
    assert result.conversion_status == "native"
    assert result.airfare_provenance.source_provider == "duffel"
    assert result.airfare_provenance.provider_offer_id == "duffel-offer-456"
    assert result.airfare_freshness.freshness_source == "provider_fetch"
