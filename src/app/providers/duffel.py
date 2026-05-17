from __future__ import annotations

from src.app.core.config import settings
from src.app.providers.base import TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest, SearchResult


class DuffelFlightsProvider(TravelProvider):
    provider_name = "duffel"
    display_name = "Duffel"
    inventory_types = (InventoryType.FLIGHT,)

    def __init__(self) -> None:
        super().__init__(timeout_seconds=settings.DUFFEL_SUPPLIER_TIMEOUT_MS / 1000.0)
        self.access_token = settings.DUFFEL_ACCESS_TOKEN

    @property
    def is_configured(self) -> bool:
        return bool(self.access_token)

    @property
    def unconfigured_reason(self) -> str | None:
        if self.is_configured:
            return None
        return "Duffel access token is not configured."

    async def search(
        self,
        request: SearchRequest,
        inventory_type: InventoryType,
    ) -> list[SearchResult]:
        if inventory_type != InventoryType.FLIGHT:
            return []
        return []
