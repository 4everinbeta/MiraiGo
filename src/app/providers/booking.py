from src.app.providers.base import TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest, SearchResult


class BookingDemandProvider(TravelProvider):
    provider_name = "booking"
    display_name = "Booking.com"
    inventory_types = (InventoryType.STAY,)

    @property
    def is_configured(self) -> bool:
        return False

    @property
    def unconfigured_reason(self) -> str | None:
        return "Booking.com Demand adapter is scaffolded but not enabled in this MVP."

    async def search(
        self, request: SearchRequest, inventory_type: InventoryType
    ) -> list[SearchResult]:
        return []
