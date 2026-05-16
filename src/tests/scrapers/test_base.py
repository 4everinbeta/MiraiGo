import pytest

from src.app.providers.base import ProviderError, TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest


class BaseProvider(TravelProvider):
    provider_name = "base"
    display_name = "Base Provider"
    inventory_types = (InventoryType.STAY,)

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        return []


@pytest.mark.asyncio
async def test_provider_healthcheck_reports_live():
    provider = BaseProvider()
    status = await provider.healthcheck()
    assert status.configured is True
    assert status.healthy is True


def test_provider_error_type():
    error = ProviderError("boom")
    assert str(error) == "boom"
