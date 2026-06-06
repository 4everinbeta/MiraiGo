import pytest
from datetime import date

from src.app.providers.expedia import ExpediaDemandProvider
from src.app.schemas.search import InventoryType, SearchRequest, SearchDateRange, TravelerCounts


@pytest.mark.asyncio
async def test_expedia_provider_is_configured_and_healthy():
    provider = ExpediaDemandProvider()
    status = await provider.healthcheck()
    assert status.configured is True
    assert status.healthy is True
    assert status.provider == "expedia"
    assert status.label == "Expedia"


@pytest.mark.asyncio
async def test_expedia_provider_search_returns_synthesized_stays():
    provider = ExpediaDemandProvider()
    results = await provider.search(
        SearchRequest(
            destination="Barcelona",
            inventory=[InventoryType.STAY],
            date_range=SearchDateRange(start=date(2026, 5, 3), end=date(2026, 5, 8)),
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.STAY,
    )
    
    assert len(results) == 3
    for r in results:
        assert r.inventory_type == InventoryType.STAY
        assert r.provider == "expedia"
        assert r.provider_label == "Expedia"
        assert r.price_known is True
        assert r.nightly_price > 0
        assert r.total_price == r.nightly_price * 5  # 5 nights
        assert r.redirect_url
        assert r.location_label == "Barcelona"
        assert len(r.amenities) > 0


@pytest.mark.asyncio
async def test_expedia_provider_search_keyword_routing():
    provider = ExpediaDemandProvider()
    
    # Mountain keyword routing
    mountain_results = await provider.search(
        SearchRequest(
            destination="Aspen Lodge",
            inventory=[InventoryType.STAY],
            date_range=SearchDateRange(start=date(2026, 5, 3), end=date(2026, 5, 5)),
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.STAY,
    )
    assert any("Alpine" in r.title or "Chalet" in r.title or "Ski" in r.title for r in mountain_results)

    # Beach keyword routing
    beach_results = await provider.search(
        SearchRequest(
            destination="Hawaii Beach",
            inventory=[InventoryType.STAY],
            date_range=SearchDateRange(start=date(2026, 5, 3), end=date(2026, 5, 5)),
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.STAY,
    )
    assert any("Beach" in r.title or "Villas" in r.title or "Seaside" in r.title for r in beach_results)

    # Historic keyword routing
    historic_results = await provider.search(
        SearchRequest(
            destination="Paris Historic Suites",
            inventory=[InventoryType.STAY],
            date_range=SearchDateRange(start=date(2026, 5, 3), end=date(2026, 5, 5)),
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.STAY,
    )
    assert any("Heritage" in r.title or "Boutique" in r.title or "Palazzo" in r.title for r in historic_results)
