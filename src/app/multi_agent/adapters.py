from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Protocol

from src.app.core.config import settings
from src.app.providers.duffel import DuffelFlightsProvider
from src.app.schemas.search import (
    FlightFilters,
    InventoryType,
    SearchDateRange,
    SearchRequest,
    TravelerCounts,
)


MOCK_SOURCE = "MOCKED_STUB_NOT_LIVE"


class PricingAdapter(Protocol):
    def search_flights(
        self,
        origin: dict[str, Any],
        destination: str,
        date_window: dict[str, Any],
        travelers: dict[str, Any],
        constraints: dict[str, Any],
    ) -> list[dict[str, Any]]:
        ...

    def search_hotels(
        self,
        destination: str,
        date_window: dict[str, Any],
        rooms: int,
        preferences: dict[str, Any],
    ) -> list[dict[str, Any]]:
        ...

    def build_package(self, flight_id: str, hotel_id: str) -> dict[str, Any]:
        ...


@dataclass
class DuffleAdapter:
    provider: DuffelFlightsProvider = DuffelFlightsProvider()

    def search_flights(
        self,
        origin: dict[str, Any],
        destination: str,
        date_window: dict[str, Any],
        travelers: dict[str, Any],
        constraints: dict[str, Any],
    ) -> list[dict[str, Any]]:
        origin_label = (origin.get("airport") or origin.get("city") or "").strip()
        start = date_window.get("start")
        if not origin_label or not destination or not start:
            return []

        request = SearchRequest(
            query=f"Flights from {origin_label} to {destination}",
            inventory=[InventoryType.FLIGHT],
            origin=origin_label,
            destination=destination,
            date_range=SearchDateRange(
                start=start,
                end=date_window.get("end"),
            ),
            travelers=TravelerCounts(
                adults=max(1, int(travelers.get("adults", 1))),
                children=max(0, int(travelers.get("children", 0))),
                infants=0,
            ),
            flight_filters=FlightFilters(
                nonstop=bool("nonstop" in (constraints.get("avoid") or [])),
            ),
            currency_code=settings.DEFAULT_CURRENCY_CODE,
            limit_per_provider=4,
        )

        try:
            offers = asyncio.run(self.provider.search(request, InventoryType.FLIGHT))
        except Exception:
            offers = []

        normalized: list[dict[str, Any]] = []
        for offer in offers:
            normalized.append(
                {
                    "id": offer.provider_offer_id or f"duffel-{offer.origin_code}-{offer.destination_code}",
                    "carrier": ",".join(offer.carrier_codes) if offer.carrier_codes else "Duffel Partner",
                    "cabin": "Economy",
                    "total_price": offer.total_price,
                    "included_bags": 1,
                    "is_mocked": False,
                    "data_source": "duffel-live",
                    "origin": origin,
                    "destination": destination,
                    "date_window": date_window,
                    "travelers": travelers,
                    "constraints": constraints,
                    "departure_at": offer.departure_at,
                    "arrival_at": offer.arrival_at,
                    "stops": offer.stops,
                }
            )
        return normalized

    def search_hotels(
        self,
        destination: str,
        date_window: dict[str, Any],
        rooms: int,
        preferences: dict[str, Any],
    ) -> list[dict[str, Any]]:
        # Flights-only adapter; hotels are delegated to hotel adapters.
        return []

    def build_package(self, flight_id: str, hotel_id: str) -> dict[str, Any]:
        return {
            "flight_id": flight_id,
            "hotel_id": hotel_id,
            "is_mocked": False,
            "data_source": "duffel-live",
        }


@dataclass
class HotelAdapter:
    def search_hotels(
        self,
        destination: str,
        date_window: dict[str, Any],
        rooms: int,
        preferences: dict[str, Any],
    ) -> list[dict[str, Any]]:
        # Placeholder adapter for Booking/Expedia/etc. Not yet wired to live inventory.
        return [
            {
                "id": f"hotel-{destination.lower().replace(' ', '-')}-value",
                "name": f"{destination} Central Hotel",
                "nightly_price": 145,
                "nights": 5,
                "total_price": 725,
                "is_mocked": True,
                "data_source": MOCK_SOURCE,
                "destination": destination,
                "date_window": date_window,
                "rooms": rooms,
                "preferences": preferences,
            },
            {
                "id": f"hotel-{destination.lower().replace(' ', '-')}-premium",
                "name": f"{destination} Grand Resort",
                "nightly_price": 245,
                "nights": 5,
                "total_price": 1225,
                "is_mocked": True,
                "data_source": MOCK_SOURCE,
                "destination": destination,
                "date_window": date_window,
                "rooms": rooms,
                "preferences": preferences,
            },
        ]

    def build_package(self, flight_id: str, hotel_id: str) -> dict[str, Any]:
        return {
            "flight_id": flight_id,
            "hotel_id": hotel_id,
            "is_mocked": True,
            "data_source": MOCK_SOURCE,
        }


@dataclass
class PricingAdapters:
    flight_adapter: DuffleAdapter = field(default_factory=DuffleAdapter)
    hotel_adapter: HotelAdapter = field(default_factory=HotelAdapter)

    def search_flights(
        self,
        origin: dict[str, Any],
        destination: str,
        date_window: dict[str, Any],
        travelers: dict[str, Any],
        constraints: dict[str, Any],
    ) -> list[dict[str, Any]]:
        live = self.flight_adapter.search_flights(
            origin=origin,
            destination=destination,
            date_window=date_window,
            travelers=travelers,
            constraints=constraints,
        )
        if live:
            return live

        # Explicit mocked fallback for development when Duffel is unavailable.
        return [
            {
                "id": f"flight-{destination.lower().replace(' ', '-')}-value",
                "carrier": "Mirai Air",
                "cabin": "Economy",
                "total_price": 640,
                "included_bags": 1,
                "is_mocked": True,
                "data_source": MOCK_SOURCE,
                "origin": origin,
                "destination": destination,
                "date_window": date_window,
                "travelers": travelers,
                "constraints": constraints,
            },
            {
                "id": f"flight-{destination.lower().replace(' ', '-')}-premium",
                "carrier": "Mirai Air",
                "cabin": "Premium Economy",
                "total_price": 920,
                "included_bags": 2,
                "is_mocked": True,
                "data_source": MOCK_SOURCE,
                "origin": origin,
                "destination": destination,
                "date_window": date_window,
                "travelers": travelers,
                "constraints": constraints,
            },
        ]

    def search_hotels(
        self,
        destination: str,
        date_window: dict[str, Any],
        rooms: int,
        preferences: dict[str, Any],
    ) -> list[dict[str, Any]]:
        return self.hotel_adapter.search_hotels(
            destination=destination,
            date_window=date_window,
            rooms=rooms,
            preferences=preferences,
        )

    def build_package(self, flight_id: str, hotel_id: str) -> dict[str, Any]:
        if flight_id.startswith("flight-") or hotel_id.startswith("hotel-"):
            return self.hotel_adapter.build_package(flight_id, hotel_id)
        return self.flight_adapter.build_package(flight_id, hotel_id)
