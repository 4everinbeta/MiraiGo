from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.app.db.session import get_db
from src.app.schemas.search import (
    FlightFilters,
    InventoryType,
    ProviderStatusResponse,
    SearchDateRange,
    SearchRequest,
    SearchResponse,
    StayFilters,
    TravelerCounts,
)
from src.app.services.search import search_service

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, db: Session = Depends(get_db)) -> SearchResponse:
    """Primary search endpoint; response may include clarification_state/weather metadata for follow-up turns."""
    return await search_service.search(request, db=db)


@router.get("/search", response_model=SearchResponse)
async def search_compat(
    q: str = Query(..., description="Natural language travel search query"),
    destination: str | None = Query(default=None),
    origin: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    max_price: float | None = Query(default=None),
    nonstop: bool = Query(default=False),
    inventory: list[InventoryType] | None = Query(default=None),
    adults: int = Query(default=1, ge=1, le=9),
    amenities: list[str] | None = Query(default=None),
    db: Session = Depends(get_db),
) -> SearchResponse:
    date_range = None
    if start_date:
        date_range = SearchDateRange(start=start_date, end=end_date)

    request = SearchRequest(
        query=q,
        destination=destination,
        origin=origin,
        date_range=date_range,
        inventory=inventory or [InventoryType.STAY, InventoryType.FLIGHT],
        travelers=TravelerCounts(adults=adults),
        stay_filters=StayFilters(max_price=max_price, amenities=amenities or []),
        flight_filters=FlightFilters(max_price=max_price, nonstop=nonstop),
    )
    return await search_service.search(request, db=db)


@router.get("/providers/status", response_model=ProviderStatusResponse)
async def provider_status() -> ProviderStatusResponse:
    return ProviderStatusResponse(providers=await search_service.provider_status())
