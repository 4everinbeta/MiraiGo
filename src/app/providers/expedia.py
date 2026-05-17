from __future__ import annotations

from src.app.providers.base import TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest, SearchResult


class ExpediaRedirectProvider(TravelProvider):
    provider_name = "expedia"
    display_name = "Expedia"
    inventory_types = (InventoryType.STAY,)

    async def search(
        self,
        request: SearchRequest,
        inventory_type: InventoryType,
    ) -> list[SearchResult]:
        if inventory_type != InventoryType.STAY:
            return []
        return []
