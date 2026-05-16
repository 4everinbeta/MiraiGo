import pytest

from src.app.providers.expedia import ExpediaRedirectProvider
from src.app.schemas.search import InventoryType, SearchRequest, TravelerCounts


@pytest.mark.asyncio
async def test_expedia_provider_returns_redirect_result():
    provider = ExpediaRedirectProvider()
    status = await provider.healthcheck()
    assert status.configured is True
    assert status.healthy is True
    assert "Redirect-only hotel handoff" in (status.reason or "")

    results = await provider.search(
        SearchRequest(
            destination="Barcelona",
            inventory=[InventoryType.STAY],
            travelers=TravelerCounts(adults=2),
        ),
        InventoryType.STAY,
    )
    assert len(results) == 1
    assert results[0].redirect_url
    assert results[0].price_known is False
