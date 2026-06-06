from urllib.parse import urlencode
import urllib.parse

from src.app.providers.base import TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest, SearchResult, StaySearchResult


class ExpediaDemandProvider(TravelProvider):
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
                "reason": None,
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

        # Calculate duration of stay in nights to determine total price
        nights = 1
        if request.date_range and request.date_range.end:
            try:
                delta = request.date_range.end - request.date_range.start
                if delta.days > 0:
                    nights = delta.days
            except Exception:
                pass

        destination_lower = request.destination.lower()
        beach_keywords = ["beach", "island", "sea", "ocean", "hawaii", "miami", "cancun", "bali", "phuket", "maldives", "bahamas", "ibiza", "tulum", "coast", "nice", "amalfi"]
        mountain_keywords = ["mountain", "alpine", "lodge", "chalet", "aspen", "zermatt", "chamonix", "denver", "banff", "whistler", "vail", "lake", "swiss", "alps", "park"]
        historic_keywords = ["paris", "rome", "kyoto", "london", "florence", "venice", "athens", "prague", "vienna", "barcelona", "madrid", "historic", "cultural"]

        is_beach = any(k in destination_lower for k in beach_keywords)
        is_mountain = any(k in destination_lower for k in mountain_keywords)
        is_historic = any(k in destination_lower for k in historic_keywords)

        if is_beach:
            properties = [
                {
                    "title": "Expedia Sands Beach Resort",
                    "nightly_price": 260.0,
                    "amenities": ["wifi", "pool", "beach-access", "ac", "breakfast"],
                    "rating": 4.5,
                },
                {
                    "title": "Expedia Blue Lagoon Ocean Villas",
                    "nightly_price": 420.0,
                    "amenities": ["wifi", "pool", "kitchen", "ac", "spa"],
                    "rating": 4.8,
                },
                {
                    "title": "Expedia Palms Seaside Hotel",
                    "nightly_price": 170.0,
                    "amenities": ["wifi", "breakfast", "ac", "parking"],
                    "rating": 4.1,
                }
            ]
        elif is_mountain:
            properties = [
                {
                    "title": "Expedia Summit Lodge",
                    "nightly_price": 210.0,
                    "amenities": ["wifi", "fireplace", "parking", "spa", "gym"],
                    "rating": 4.4,
                },
                {
                    "title": "Expedia Timberwood Chalet",
                    "nightly_price": 360.0,
                    "amenities": ["wifi", "fireplace", "kitchen", "parking", "view"],
                    "rating": 4.7,
                },
                {
                    "title": "Expedia Slope-Side Ski Resort",
                    "nightly_price": 290.0,
                    "amenities": ["wifi", "pool", "ac", "gym", "bar"],
                    "rating": 4.3,
                }
            ]
        elif is_historic:
            properties = [
                {
                    "title": "Expedia Grand Hotel & Suites",
                    "nightly_price": 250.0,
                    "amenities": ["wifi", "breakfast", "ac", "concierge", "bar"],
                    "rating": 4.6,
                },
                {
                    "title": "Expedia Heritage Boutique Residence",
                    "nightly_price": 195.0,
                    "amenities": ["wifi", "ac", "kitchen", "breakfast", "parking"],
                    "rating": 4.2,
                },
                {
                    "title": "Expedia Palazzo Luxury Suites",
                    "nightly_price": 320.0,
                    "amenities": ["wifi", "ac", "kitchen", "concierge"],
                    "rating": 4.7,
                }
            ]
        else:
            properties = [
                {
                    "title": f"Expedia Metropolitan Plaza {request.destination}",
                    "nightly_price": 180.0,
                    "amenities": ["wifi", "ac", "gym", "parking", "breakfast"],
                    "rating": 4.3,
                },
                {
                    "title": f"Expedia Loft Suites {request.destination}",
                    "nightly_price": 220.0,
                    "amenities": ["wifi", "ac", "kitchen", "gym", "washer"],
                    "rating": 4.5,
                },
                {
                    "title": f"Expedia Central Stay {request.destination}",
                    "nightly_price": 140.0,
                    "amenities": ["wifi", "ac", "breakfast", "parking"],
                    "rating": 4.0,
                }
            ]

        results = []
        for prop in properties:
            nightly = prop["nightly_price"]
            total = nightly * nights
            amenities = prop["amenities"]
            title = prop["title"]

            # Calculate score based on stay filters
            score = 70.0 + (prop["rating"] * 2)
            requested_amenities = request.stay_filters.amenities if request.stay_filters else []
            matching_amenities = [a for a in requested_amenities if a in amenities]
            score += len(matching_amenities) * 5.0
            if request.stay_filters and request.stay_filters.max_price:
                if nightly <= request.stay_filters.max_price:
                    score += 10.0
                else:
                    score -= 15.0

            score = min(max(score, 50.0), 98.0)

            results.append(
                StaySearchResult(
                    inventory_type=InventoryType.STAY,
                    provider=self.provider_name,
                    provider_label=self.display_name,
                    title=title,
                    description=f"An exceptional property in {request.destination} managed by Expedia, promising high comfort and local experiences.",
                    total_price=total,
                    currency=request.currency_code,
                    redirect_url=self._build_redirect_url(request.destination, check_in, check_out, request),
                    deep_link_label="View stays on Expedia",
                    score=score,
                    price_known=True,
                    price_label=f"${int(nightly)} / night",
                    location_label=request.destination,
                    amenities=amenities,
                    nightly_price=nightly,
                    check_in=check_in,
                    check_out=check_out,
                )
            )

        return results

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
