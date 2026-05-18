import pytest

from src.app.providers.base import TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest, StaySearchResult
from src.app.services.search import search_service


class CacheProvider(TravelProvider):
    provider_name = "cache"
    display_name = "Cache Provider"
    inventory_types = (InventoryType.STAY,)

    def __init__(self):
        super().__init__()
        self.calls = 0

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        self.calls += 1
        return [
            StaySearchResult(
                inventory_type=InventoryType.STAY,
                provider=self.provider_name,
                provider_label=self.display_name,
                title="Cached Result",
                description="from provider",
                total_price=400,
                currency="USD",
                redirect_url="https://example.com/stay",
                deep_link_label="Continue search",
                score=45,
                location_label="Rome",
                amenities=["wifi"],
                nightly_price=100,
                check_in=None,
                check_out=None,
            )
        ]


@pytest.mark.asyncio
async def test_provider_results_are_cached(fake_redis):
    provider = CacheProvider()
    search_service.providers = [provider]
    request = SearchRequest(
        query="Rome stay",
        destination="Rome",
        inventory=[InventoryType.STAY],
    )

    await search_service.search(request)
    await search_service.search(request)

    assert provider.calls == 1
