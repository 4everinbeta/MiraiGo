from datetime import date

from src.app.schemas.search import InventoryType, SearchDateRange, SearchRequest
from src.app.services.search import SearchService


def test_duffel_fallback_requests_are_deterministic():
    service = SearchService()
    request = SearchRequest(
        query="Flights to Lisbon",
        destination="Lisbon",
        origin="Denver",
        inventory=[InventoryType.FLIGHT],
        date_range=SearchDateRange(start=date(2026, 6, 10), end=date(2026, 6, 17)),
        flight_filters={"nonstop": True},
    )

    fallbacks = service._duffel_fallback_requests(request)

    assert [label for label, _ in fallbacks] == ["relax_nonstop_filter", "widen_date_window"]
    relaxed_request = fallbacks[0][1]
    widened_request = fallbacks[1][1]
    assert relaxed_request.flight_filters.nonstop is False
    assert widened_request.date_range.start.isoformat() == "2026-06-08"
    assert widened_request.date_range.end.isoformat() == "2026-06-19"
