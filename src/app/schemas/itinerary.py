from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from src.app.schemas.search import (
    ClarificationBudgetRange,
    ClarificationQuestion,
    ClarificationSlotState,
    SearchDateRange,
    TravelerCounts,
)


class ItineraryCostEstimate(BaseModel):
    total_estimated: float = Field(ge=0)
    flight_estimated: float = Field(ge=0)
    stay_estimated: float = Field(ge=0)
    car_estimated: float = Field(ge=0)
    currency_code: str = Field(default="USD", min_length=3, max_length=3)
    confidence: Literal["low", "medium", "high"] = "medium"


class ItineraryProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid4()))
    destination: str
    destination_region_key: str
    travel_window: SearchDateRange
    duration_nights: int = Field(ge=1)
    travelers: TravelerCounts
    needs_car: bool = False
    cost_estimate: ItineraryCostEstimate
    rationale: str
    within_budget: bool = True
    over_budget_note: str | None = None


class ItineraryProposeRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    travelers: TravelerCounts | None = None
    budget_range: ClarificationBudgetRange | None = None
    candidate_destinations: list[str] = Field(default_factory=list)
    travel_window: SearchDateRange | None = None
    include_car: bool | None = None
    clarification_answer: dict | None = None
    currency_code: str = Field(default="USD", min_length=3, max_length=3)


class ItineraryProposeResponse(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    proposals: list[ItineraryProposal] = Field(default_factory=list)
    clarification_state: list[ClarificationSlotState] = Field(default_factory=list)
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list)
    applied_inputs: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class ItineraryPriceRequest(BaseModel):
    proposal_id: str
    proposal_snapshot: ItineraryProposal
    travelers: TravelerCounts
    currency_code: str = Field(default="USD", min_length=3, max_length=3)


class ItineraryPriceResponse(BaseModel):
    search_id: str = Field(default_factory=lambda: str(uuid4()))
    proposal_id: str
    flight_results: list[dict] = Field(default_factory=list)
    stay_results: list[dict] = Field(default_factory=list)
    car_redirect_url: str | None = None
    car_redirect_label: str | None = None
    provider_status: list[dict] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
