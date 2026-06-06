import pytest

from src.app.providers.expedia import ExpediaDemandProvider
from src.app.schemas.search import InventoryType, SearchRequest, TravelerCounts


@pytest.mark.asyncio
async def test_expedia_provider_returns_synthesized_results():
    provider = ExpediaDemandProvider()
    status = await provider.healthcheck()
    assert status.configured is True
    assert status.healthy is True

    results = await provider.search(
        SearchRequest(
            destination="Barcelona",
            inventory=[InventoryType.STAY],
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.STAY,
    )
    assert len(results) == 3
    assert results[0].redirect_url
    assert results[0].price_known is True
