from __future__ import annotations

import asyncio
from datetime import date

import pytest

from src.app.providers.base import ProviderError, TravelProvider
from src.app.schemas.search import (
    ClarificationBudgetRange,
    FlightSearchResult,
    InventoryType,
    SearchDateRange,
    SearchRequest,
)
from src.app.services.search import SearchService


def _flight_result(provider: str, label: str, score: float, price: float) -> FlightSearchResult:
    return FlightSearchResult(
        inventory_type=InventoryType.FLIGHT,
        provider=provider,
        provider_label=label,
        title="DEN to LIS",
        description=f"{label} sample offer",
        total_price=price,
        currency="USD",
        score=score,
        origin_code="DEN",
        destination_code="LIS",
        departure_at="2026-06-10T09:00:00",
        arrival_at="2026-06-10T19:00:00",
        carrier_codes=["XX"],
        stops=0,
        duration="PT10H",
    )


@pytest.fixture(autouse=True)
def disable_search_cache(monkeypatch):
    monkeypatch.setattr("src.app.services.search.redis_client.get", lambda *args, **kwargs: None)
    monkeypatch.setattr("src.app.services.search.redis_client.setex", lambda *args, **kwargs: True)


class FakeFlightProvider(TravelProvider):
    provider_name = "fake"
    display_name = "Fake"
    inventory_types = (InventoryType.FLIGHT,)

    def __init__(
        self,
        *,
        provider_name: str,
        display_name: str,
        results: list[FlightSearchResult] | None = None,
        configured: bool = True,
        delay_seconds: float = 0.0,
        error_message: str | None = None,
    ) -> None:
        super().__init__(timeout_seconds=0.05, max_retries=0)
        self.provider_name = provider_name
        self.display_name = display_name
        self._configured = configured
        self._results = results or []
        self._delay_seconds = delay_seconds
        self._error_message = error_message
        self.search_calls = 0

    @property
    def is_configured(self) -> bool:
        return self._configured

    @property
    def unconfigured_reason(self) -> str | None:
        if self._configured:
            return None
        return f"{self.display_name} is not configured."

    async def search(
        self, request: SearchRequest, inventory_type: InventoryType
    ) -> list[FlightSearchResult]:
        self.search_calls += 1
        if self._delay_seconds:
            await asyncio.sleep(self._delay_seconds)
        if self._error_message:
            raise ProviderError(self._error_message)
        return list(self._results)


def _resolved_flight_request() -> SearchRequest:
    return SearchRequest(
        query="Flight options to Lisbon",
        inventory=[InventoryType.FLIGHT],
        destination="LIS",
        date_range=SearchDateRange(start=date(2026, 6, 10), end=date(2026, 6, 17)),
        trip_length_days=7,
        budget_range=ClarificationBudgetRange(
            minimum=1000, maximum=2500, currency_code="USD"
        ),
    )


@pytest.mark.asyncio
async def test_visible_flight_gate_requires_origin_destination_and_dates():
    service = SearchService()
    service.providers = [
        FakeFlightProvider(
            provider_name="amadeus",
            display_name="Amadeus",
            results=[_flight_result("amadeus", "Amadeus", score=10.0, price=500.0)],
        )
    ]
    request = _resolved_flight_request()

    response = await service.search(request)

    assert response.results == []
    assert any("flight" in warning.lower() and "origin" in warning.lower() for warning in response.warnings)


@pytest.mark.asyncio
async def test_prefetch_requires_destination_and_timeline_without_bypassing_visible_gate():
    service = SearchService()
    provider = FakeFlightProvider(
        provider_name="amadeus",
        display_name="Amadeus",
        results=[_flight_result("amadeus", "Amadeus", score=10.0, price=500.0)],
    )
    service.providers = [provider]

    prefetch_eligible_request = SearchRequest(
        query="Need flights to Lisbon in June",
        inventory=[InventoryType.FLIGHT],
        destination="LIS",
        date_range=SearchDateRange(start=date(2026, 6, 10), end=date(2026, 6, 17)),
    )
    response = await service.search(prefetch_eligible_request)

    assert response.results == []
    assert provider.search_calls == 1

    no_timeline_request = SearchRequest(
        query="Need flights to Lisbon",
        inventory=[InventoryType.FLIGHT],
        destination="LIS",
    )
    response_without_timeline = await service.search(no_timeline_request)

    assert response_without_timeline.results == []
    assert provider.search_calls == 1


@pytest.mark.asyncio
async def test_dual_provider_interleave_is_deterministic():
    service = SearchService()
    service.providers = [
        FakeFlightProvider(
            provider_name="amadeus",
            display_name="Amadeus",
            results=[
                _flight_result("amadeus", "Amadeus", score=95.0, price=410.0),
                _flight_result("amadeus", "Amadeus", score=70.0, price=450.0),
            ],
        ),
        FakeFlightProvider(
            provider_name="duffel",
            display_name="Duffel",
            results=[
                _flight_result("duffel", "Duffel", score=90.0, price=430.0),
                _flight_result("duffel", "Duffel", score=65.0, price=490.0),
            ],
        ),
    ]
    request = _resolved_flight_request().model_copy(update={"origin": "DEN"})

    first = await service.search(request)
    second = await service.search(request)

    first_order = [f"{item.provider}:{item.score}" for item in first.results]
    second_order = [f"{item.provider}:{item.score}" for item in second.results]
    assert first_order == ["amadeus:95.0", "duffel:90.0", "amadeus:70.0", "duffel:65.0"]
    assert second_order == first_order
    first_ids = [item.normalized_offer_id for item in first.results]
    second_ids = [item.normalized_offer_id for item in second.results]
    assert all(offer_id is not None for offer_id in first_ids)
    assert first_ids == second_ids
    for item in first.results:
        assert item.airfare_provenance.source_provider == item.provider
        assert item.airfare_freshness.freshness_source in {"provider_fetch", "provider_quote", None}
        assert isinstance(item.missing_fields, list)


@pytest.mark.asyncio
async def test_flight_normalization_keeps_null_contract_for_missing_fields():
    service = SearchService()
    service.providers = [
        FakeFlightProvider(
            provider_name="amadeus",
            display_name="Amadeus",
            results=[
                _flight_result(
                    "amadeus",
                    "Amadeus",
                    score=95.0,
                    price=410.0,
                ).model_copy(
                    update={
                        "departure_at": "",
                        "arrival_at": "",
                        "duration": None,
                    }
                )
            ],
        )
    ]
    request = _resolved_flight_request().model_copy(update={"origin": "DEN"})

    response = await service.search(request)

    offer = response.results[0]
    assert offer.duration_minutes is None
    assert offer.stops_count == 0
    assert "departure_at" in offer.missing_fields
    assert "arrival_at" in offer.missing_fields
    assert "duration_minutes" in offer.missing_fields


@pytest.mark.asyncio
async def test_flight_normalization_keeps_legacy_fields_for_compatibility():
    service = SearchService()
    service.providers = [
        FakeFlightProvider(
            provider_name="amadeus",
            display_name="Amadeus",
            results=[_flight_result("amadeus", "Amadeus", score=90.0, price=410.0)],
        )
    ]
    request = _resolved_flight_request().model_copy(update={"origin": "DEN"})

    response = await service.search(request)

    offer = response.results[0]
    assert offer.total_price == 410.0
    assert offer.currency == "USD"
    assert offer.stops == 0
    assert offer.duration == "PT10H"
    assert offer.price_minor == 41000
    assert offer.currency_code == "USD"


@pytest.mark.asyncio
async def test_partial_failure_returns_other_provider_results():
    service = SearchService()
    service.providers = [
        FakeFlightProvider(
            provider_name="amadeus",
            display_name="Amadeus",
            results=[_flight_result("amadeus", "Amadeus", score=88.0, price=420.0)],
        ),
        FakeFlightProvider(
            provider_name="duffel",
            display_name="Duffel",
            error_message="supplier outage",
        ),
    ]
    request = _resolved_flight_request().model_copy(update={"origin": "DEN"})

    response = await service.search(request)

    assert [result.provider for result in response.results] == ["amadeus"]
    assert any("Duffel flight search unavailable: supplier outage" in warning for warning in response.warnings)
    duffel_status = next(status for status in response.provider_status if status.provider == "duffel")
    assert duffel_status.healthy is False
    assert duffel_status.reason == "supplier outage"


@pytest.mark.asyncio
async def test_provider_timeout_returns_partial_success_with_warning():
    service = SearchService()
    service.providers = [
        FakeFlightProvider(
            provider_name="amadeus",
            display_name="Amadeus",
            results=[_flight_result("amadeus", "Amadeus", score=90.0, price=410.0)],
        ),
        FakeFlightProvider(
            provider_name="duffel",
            display_name="Duffel",
            delay_seconds=0.3,
        ),
    ]
    request = _resolved_flight_request().model_copy(update={"origin": "DEN"})

    response = await service.search(request)

    assert [result.provider for result in response.results] == ["amadeus"]
    assert any("timed out after" in warning for warning in response.warnings)


@pytest.mark.asyncio
async def test_interleave_tiebreak_uses_provider_registry_order():
    service = SearchService()
    service.providers = [
        FakeFlightProvider(
            provider_name="amadeus",
            display_name="Amadeus",
            results=[_flight_result("amadeus", "Amadeus", score=80.0, price=400.0)],
        ),
        FakeFlightProvider(
            provider_name="duffel",
            display_name="Duffel",
            results=[_flight_result("duffel", "Duffel", score=80.0, price=410.0)],
        ),
    ]
    request = _resolved_flight_request().model_copy(update={"origin": "DEN"})

    response = await service.search(request)

    assert [result.provider for result in response.results] == ["amadeus", "duffel"]
