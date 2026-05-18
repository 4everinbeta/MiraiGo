from urllib.parse import urlencode

from src.app.providers.base import TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest, SearchResult, StaySearchResult


class ExpediaRedirectProvider(TravelProvider):
    provider_name = "expedia"
    display_name = "Expedia"
    inventory_types = (InventoryType.STAY,)

    @property
    def is_configured(self) -> bool:
        return True

    @property
    def unconfigured_reason(self) -> str | None:
        return None

    async def healthcheck(self):
        status = await super().healthcheck()
        return status.model_copy(
            update={
                "healthy": True,
                "reason": "Redirect-only hotel handoff. Live rates open on Expedia.",
            }
        )

    async def search(
        self, request: SearchRequest, inventory_type: InventoryType
    ) -> list[SearchResult]:
        if inventory_type != InventoryType.STAY or not request.destination:
            return []

        check_in = request.date_range.start.isoformat() if request.date_range else None
        check_out = (
            request.date_range.end.isoformat()
            if request.date_range and request.date_range.end
            else None
        )
        requested_amenities = request.stay_filters.amenities[:4]

        return [
            StaySearchResult(
                inventory_type=InventoryType.STAY,
                provider=self.provider_name,
                provider_label=self.display_name,
                title=f"Hotels in {request.destination}",
                description="Open Expedia to see live hotel inventory and current partner pricing.",
                total_price=0,
                currency=request.currency_code,
                redirect_url=self._build_redirect_url(request.destination, check_in, check_out, request),
                deep_link_label="View stays on Expedia",
                score=45 + (len(requested_amenities) * 5),
                price_known=False,
                price_label="Check live rates on Expedia",
                location_label=request.destination,
                amenities=requested_amenities,
                nightly_price=None,
                check_in=check_in,
                check_out=check_out,
            )
        ]

    def _build_redirect_url(
        self,
        destination: str,
        check_in: str | None,
        check_out: str | None,
        request: SearchRequest,
    ) -> str:
        params = {
            "destination": destination,
            "adults": request.travelers.adults,
            "rooms": 1,
        }
        if check_in:
            params["startDate"] = check_in
        if check_out:
            params["endDate"] = check_out
        return f"https://www.expedia.com/Hotel-Search?{urlencode(params)}"
