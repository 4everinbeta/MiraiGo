from src.app.providers.base import TravelProvider
from src.app.schemas.search import InventoryType, SearchRequest, SearchResult, StaySearchResult
from src.app.scrapers.booking import BookingScraper


class BookingDemandProvider(TravelProvider):
    provider_name = "booking"
    display_name = "Booking.com"
    inventory_types = (InventoryType.STAY,)

    @property
    def is_configured(self) -> bool:
        return True

    @property
    def unconfigured_reason(self) -> str | None:
        return None

    async def search(
        self, request: SearchRequest, inventory_type: InventoryType
    ) -> list[SearchResult]:
        if inventory_type != InventoryType.STAY or not request.destination:
            return []

        scraper = BookingScraper()
        scrape_result = await scraper.scrape(request.destination)
        results = []

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

        for raw in scrape_result.get("results", []):
            nightly = float(raw.get("price", 150))
            total = nightly * nights
            amenities = raw.get("amenities", ["wifi"])
            
            # Match traveler and stay filters criteria to calculate score
            score = 75.0
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
                    title=raw.get("text", "Premium Stay"),
                    description=f"A beautiful property in {request.destination} offering top-tier comfort, perfect for your travel plans.",
                    total_price=total,
                    currency=request.currency_code,
                    redirect_url=raw.get("link") or f"https://www.booking.com/searchresults.html?ss={request.destination}",
                    deep_link_label="View stays on Booking.com",
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
