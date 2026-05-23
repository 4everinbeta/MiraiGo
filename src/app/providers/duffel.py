from __future__ import annotations

from src.app.core.config import settings
from src.app.providers.base import ProviderError, TravelProvider
from src.app.schemas.search import FlightSearchResult, InventoryType, SearchRequest, SearchResult


class DuffelFlightsProvider(TravelProvider):
    provider_name = "duffel"
    display_name = "Duffel"
    inventory_types = (InventoryType.FLIGHT,)

    def __init__(self) -> None:
        super().__init__(
            timeout_seconds=max(settings.PROVIDER_TIMEOUT_SECONDS, 15.0),
            max_retries=settings.PROVIDER_MAX_RETRIES,
        )
        self.base_url = settings.DUFFEL_API_URL.rstrip("/")
        self.api_version = settings.DUFFEL_API_VERSION
        self.access_token = settings.DUFFEL_ACCESS_TOKEN
        self.supplier_timeout_ms = settings.DUFFEL_SUPPLIER_TIMEOUT_MS

    @property
    def is_configured(self) -> bool:
        return bool(self.access_token)

    @property
    def unconfigured_reason(self) -> str | None:
        if self.is_configured:
            return None
        return "Duffel access token is not configured."

    async def healthcheck(self):
        status = await super().healthcheck()
        if not self.is_configured:
            return status
        try:
            await self._resolve_place_code("london")
            return status.model_copy(update={"healthy": True, "reason": None})
        except ProviderError as exc:
            return status.model_copy(update={"healthy": False, "reason": str(exc)})

    async def search(
        self, request: SearchRequest, inventory_type: InventoryType
    ) -> list[SearchResult]:
        if inventory_type != InventoryType.FLIGHT or not self.is_configured:
            return []
        if request.travelers.children or request.travelers.infants:
            raise ProviderError(
                "Duffel flight search in this MVP supports adults only because child ages are not captured yet."
            )
        if not request.origin or not request.destination:
            return []
        if not request.date_range or not request.date_range.start:
            return []

        origin_code = await self._resolve_place_code(request.origin)
        destination_code = await self._resolve_place_code(request.destination)
        if not origin_code or not destination_code:
            return []

        response = await self._create_offer_request(
            self._build_offer_request_payload(request, origin_code, destination_code)
        )
        offers = response.get("data", {}).get("offers", [])
        results: list[SearchResult] = []
        for offer in offers[: request.limit_per_provider]:
            result = self._offer_to_result(offer, request, origin_code, destination_code)
            if result is not None:
                results.append(result)
        return results

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Duffel-Version": self.api_version,
            "Authorization": f"Bearer {self.access_token}",
        }

    async def _place_suggestions(self, query: str) -> dict:
        return await self.request(
            "GET",
            f"{self.base_url}/places/suggestions",
            headers=self._headers(),
            params={"query": query},
        )

    async def _resolve_place_code(self, location: str | None) -> str | None:
        if not location:
            return None
        clean = location.strip()
        if len(clean) == 3 and clean.isalpha():
            return clean.upper()

        response = await self._place_suggestions(clean)
        for place in response.get("data", []):
            iata_code = place.get("iata_code")
            if iata_code:
                return iata_code.upper()
        return None

    def _build_offer_request_payload(
        self, request: SearchRequest, origin_code: str, destination_code: str
    ) -> dict:
        slices = [
            {
                "origin": origin_code,
                "destination": destination_code,
                "departure_date": request.date_range.start.isoformat(),
            }
        ]
        if request.date_range and request.date_range.end:
            slices.append(
                {
                    "origin": destination_code,
                    "destination": origin_code,
                    "departure_date": request.date_range.end.isoformat(),
                }
            )

        data: dict[str, object] = {
            "slices": slices,
            "passengers": [{"type": "adult"} for _ in range(request.travelers.adults)],
        }
        if request.flight_filters.nonstop:
            data["max_connections"] = 0
        return {"data": data}

    async def _create_offer_request(self, payload: dict) -> dict:
        return await self.request(
            "POST",
            f"{self.base_url}/air/offer_requests",
            headers=self._headers(),
            params={
                "return_offers": "true",
                "supplier_timeout": str(self.supplier_timeout_ms),
            },
            json=payload,
        )

    def _offer_to_result(
        self,
        offer: dict,
        request: SearchRequest,
        origin_code: str,
        destination_code: str,
    ) -> FlightSearchResult | None:
        slices = offer.get("slices", [])
        if not slices:
            return None

        first_slice = slices[0]
        segments = first_slice.get("segments", [])
        if not segments:
            return None

        first_segment = segments[0]
        last_segment = segments[-1]
        slice_stops = first_slice.get("stops")
        if not isinstance(slice_stops, int) or slice_stops < 0:
            slice_stops = max(0, len(segments) - 1)
        carrier_codes = sorted(
            {
                segment.get("operating_carrier", {}).get("iata_code")
                or segment.get("marketing_carrier", {}).get("iata_code")
                for segment in segments
                if segment.get("operating_carrier") or segment.get("marketing_carrier")
            }
            - {None}
        )
        carrier_names = sorted(
            {
                segment.get("operating_carrier", {}).get("name")
                or segment.get("marketing_carrier", {}).get("name")
                for segment in segments
                if segment.get("operating_carrier") or segment.get("marketing_carrier")
            }
            - {None}
        )

        total_price = float(offer.get("total_amount", 0.0))
        total_currency = offer.get("total_currency", request.currency_code)
        owner_name = offer.get("owner", {}).get("name") or self.display_name
        description = owner_name
        if carrier_names:
            description = f"{owner_name} via {' / '.join(carrier_names)}"

        trip_label = f"{origin_code} to {destination_code}"
        if request.date_range and request.date_range.end:
            trip_label = f"{trip_label} roundtrip"

        return FlightSearchResult(
            inventory_type=InventoryType.FLIGHT,
            provider=self.provider_name,
            provider_label=self.display_name,
            title=trip_label,
            description=description,
            total_price=total_price,
            currency=total_currency,
            redirect_url=None,
            deep_link_label=None,
            score=self._flight_score(total_price, len(segments) - 1),
            origin_code=first_segment.get("origin", {}).get("iata_code", origin_code),
            destination_code=last_segment.get("destination", {}).get(
                "iata_code", destination_code
            ),
            departure_at=first_segment.get("departing_at", ""),
            arrival_at=last_segment.get("arriving_at", ""),
            carrier_codes=carrier_codes,
            stops=slice_stops,
            duration=first_slice.get("duration"),
            provider_offer_id=offer.get("id"),
        )

    def _flight_score(self, price: float, stops: int) -> float:
        return max(1.0, 1000.0 / max(price, 1.0) - (stops * 25))
