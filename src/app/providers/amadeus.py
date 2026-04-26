from __future__ import annotations

from typing import Any

import httpx

from src.app.core.config import settings
from src.app.db import redis as redis_store
from src.app.providers.base import ProviderError, TravelProvider
from src.app.schemas.search import FlightSearchResult, InventoryType, SearchRequest, SearchResult


class AmadeusFlightsProvider(TravelProvider):
    provider_name = "amadeus"
    display_name = "Amadeus"
    inventory_types = (InventoryType.FLIGHT,)

    def __init__(self) -> None:
        super().__init__(
            timeout_seconds=max(
                settings.AMADEUS_REQUEST_DEADLINE_SECONDS, settings.PROVIDER_TIMEOUT_SECONDS
            ),
            max_retries=1,
        )
        self.api_url = settings.AMADEUS_API_URL.rstrip("/")
        self.client_id = settings.AMADEUS_CLIENT_ID
        self.client_secret = settings.AMADEUS_CLIENT_SECRET
        self.token_safety_buffer_seconds = max(
            0, settings.AMADEUS_TOKEN_SAFETY_BUFFER_SECONDS
        )
        self.token_cache_key = settings.AMADEUS_TOKEN_CACHE_KEY

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.api_url)

    @property
    def unconfigured_reason(self) -> str | None:
        if self.is_configured:
            return None
        return "Amadeus credentials are not configured."

    async def search(
        self, request: SearchRequest, inventory_type: InventoryType
    ) -> list[SearchResult]:
        if inventory_type != InventoryType.FLIGHT or not self.is_configured:
            return []
        if not request.origin or not request.destination:
            return []
        if not request.date_range or not request.date_range.start:
            return []

        origin_code = self._normalize_iata(request.origin)
        destination_code = self._normalize_iata(request.destination)
        if not origin_code or not destination_code:
            return []

        params = {
            "originLocationCode": origin_code,
            "destinationLocationCode": destination_code,
            "departureDate": request.date_range.start.isoformat(),
            "adults": str(request.travelers.adults),
            "nonStop": str(request.flight_filters.nonstop).lower(),
            "max": str(request.limit_per_provider),
            "currencyCode": request.currency_code,
        }
        if request.date_range.end:
            params["returnDate"] = request.date_range.end.isoformat()

        payload = await self._search_flight_offers(params)
        offers = payload.get("data", [])
        results: list[SearchResult] = []
        for offer in offers[: request.limit_per_provider]:
            mapped = self._offer_to_result(offer, request, origin_code, destination_code)
            if mapped is not None:
                results.append(mapped)
        return results

    async def _search_flight_offers(self, params: dict[str, str]) -> dict[str, Any]:
        token = await self._get_oauth_token()
        status_code, payload = await self._flight_offers_request(token, params)
        if status_code == 401:
            token = await self._get_oauth_token(force_refresh=True)
            status_code, payload = await self._flight_offers_request(token, params)
        if status_code == 401:
            raise ProviderError("Amadeus authorization failed after token refresh.")
        if status_code >= 400:
            raise ProviderError(
                f"Amadeus flight-offers request failed with status {status_code}."
            )
        return payload

    async def _get_oauth_token(self, force_refresh: bool = False) -> str:
        if not force_refresh:
            cached = redis_store.redis_client.get(self.token_cache_key)
            if cached:
                return cached

        token_url = f"{self.api_url}/v1/security/oauth2/token"
        form_payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id or "",
            "client_secret": self.client_secret or "",
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                token_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=form_payload,
            )

        if response.status_code >= 400:
            raise ProviderError(
                f"Amadeus authentication failed with status {response.status_code}."
            )

        payload = response.json()
        access_token = payload.get("access_token")
        expires_in = int(payload.get("expires_in", 0))
        if not access_token:
            raise ProviderError("Amadeus authentication response missing access token.")

        token_ttl = max(1, expires_in - self.token_safety_buffer_seconds)
        redis_store.redis_client.setex(self.token_cache_key, token_ttl, access_token)
        return access_token

    async def _flight_offers_request(
        self, token: str, params: dict[str, str]
    ) -> tuple[int, dict[str, Any]]:
        offers_url = f"{self.api_url}/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(offers_url, headers=headers, params=params)

        if response.status_code == 401:
            return response.status_code, {}
        if response.status_code >= 400:
            return response.status_code, {}
        return response.status_code, response.json()

    def _offer_to_result(
        self,
        offer: dict[str, Any],
        request: SearchRequest,
        origin_code: str,
        destination_code: str,
    ) -> FlightSearchResult | None:
        itineraries = offer.get("itineraries", [])
        if not itineraries:
            return None

        first_itinerary = itineraries[0]
        segments = first_itinerary.get("segments", [])
        if not segments:
            return None

        first_segment = segments[0]
        last_segment = segments[-1]
        carrier_codes = sorted(
            {segment.get("carrierCode") for segment in segments if segment.get("carrierCode")}
        )
        price_data = offer.get("price", {})
        total_price = float(price_data.get("total", 0.0))
        total_currency = price_data.get("currency", request.currency_code)

        trip_label = f"{origin_code} to {destination_code}"
        if request.date_range and request.date_range.end:
            trip_label = f"{trip_label} roundtrip"

        return FlightSearchResult(
            inventory_type=InventoryType.FLIGHT,
            provider=self.provider_name,
            provider_label=self.display_name,
            title=trip_label,
            description=self.display_name,
            total_price=total_price,
            currency=total_currency,
            redirect_url=None,
            deep_link_label=None,
            score=self._flight_score(total_price, len(segments) - 1),
            origin_code=first_segment.get("departure", {}).get("iataCode", origin_code),
            destination_code=last_segment.get("arrival", {}).get(
                "iataCode", destination_code
            ),
            departure_at=first_segment.get("departure", {}).get("at", ""),
            arrival_at=last_segment.get("arrival", {}).get("at", ""),
            carrier_codes=carrier_codes,
            stops=max(0, len(segments) - 1),
            duration=first_itinerary.get("duration"),
        )

    def _normalize_iata(self, raw_code: str | None) -> str | None:
        if not raw_code:
            return None
        code = raw_code.strip().upper()
        if len(code) != 3 or not code.isalpha():
            return None
        return code

    def _flight_score(self, price: float, stops: int) -> float:
        return max(1.0, 1000.0 / max(price, 1.0) - (stops * 25))
