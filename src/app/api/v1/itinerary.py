from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.db.session import get_db
from src.app.schemas.itinerary import (
    ItineraryPriceRequest,
    ItineraryPriceResponse,
    ItineraryProposeRequest,
    ItineraryProposeResponse,
)
from src.app.services.itinerary import itinerary_service

router = APIRouter(prefix="/itinerary", tags=["itinerary"])


@router.post("/propose", response_model=ItineraryProposeResponse)
async def propose_itinerary(request: ItineraryProposeRequest) -> ItineraryProposeResponse:
    return await itinerary_service.propose(request)


@router.post("/price", response_model=ItineraryPriceResponse)
async def price_itinerary(
    request: ItineraryPriceRequest,
    db: Session = Depends(get_db),
) -> ItineraryPriceResponse:
    _ = db
    return await itinerary_service.price_proposal(request)
