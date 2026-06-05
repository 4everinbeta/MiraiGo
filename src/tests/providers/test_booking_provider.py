import pytest

from src.app.providers.booking import BookingDemandProvider
from src.app.schemas.search import InventoryType, SearchRequest, TravelerCounts


@pytest.mark.asyncio
async def test_booking_provider_is_configured_and_healthy():
    provider = BookingDemandProvider()
    status = await provider.healthcheck()
    assert status.configured is True
    assert status.healthy is True
    assert status.provider == "booking"
    assert status.label == "Booking.com"


@pytest.mark.asyncio
async def test_booking_provider_search_returns_live_stays():
    provider = BookingDemandProvider()
    results = await provider.search(
        SearchRequest(
            destination="Barcelona",
            inventory=[InventoryType.STAY],
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.STAY,
    )
    
    assert len(results) > 0
    for r in results:
        assert r.inventory_type == InventoryType.STAY
        assert r.provider == "booking"
        assert r.provider_label == "Booking.com"
        assert r.price_known is True
        assert r.nightly_price > 0
        assert r.total_price > 0
        assert r.redirect_url
        assert r.location_label == "Barcelona"


@pytest.mark.asyncio
async def test_booking_provider_search_keyword_routing():
    provider = BookingDemandProvider()
    
    # Mountain keyword routing
    mountain_results = await provider.search(
        SearchRequest(
            destination="Aspen Mountains",
            inventory=[InventoryType.STAY],
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.STAY,
    )
    assert any("Alpine" in r.title or "Chalet" in r.title or "Ski" in r.title for r in mountain_results)

    # Beach keyword routing
    beach_results = await provider.search(
        SearchRequest(
            destination="Miami Beach",
            inventory=[InventoryType.STAY],
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.STAY,
    )
    assert any("Beach" in r.title or "Villas" in r.title or "Seaside" in r.title for r in beach_results)
