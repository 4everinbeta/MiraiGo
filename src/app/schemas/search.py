from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class InventoryType(str, Enum):
    STAY = "stay"
    FLIGHT = "flight"


class SearchDateRange(BaseModel):
    start: date
    end: date | None = None

    @model_validator(mode="after")
    def validate_range(self) -> "SearchDateRange":
        if self.end and self.end < self.start:
            raise ValueError("End date must not be earlier than start date.")
        return self


class TravelerCounts(BaseModel):
    adults: int = Field(default=1, ge=1, le=9)
    children: int = Field(default=0, ge=0, le=8)
    infants: int = Field(default=0, ge=0, le=4)


class StayFilters(BaseModel):
    max_price: float | None = Field(default=None, gt=0)
    amenities: list[str] = Field(default_factory=list)


class FlightFilters(BaseModel):
    max_price: float | None = Field(default=None, gt=0)
    nonstop: bool = False


class ClarificationSlot(str, Enum):
    DESTINATION = "destination"
    TIMELINE = "timeline"
    TRIP_LENGTH = "trip_length"
    BUDGET = "budget"


class ClarificationBudgetRange(BaseModel):
    minimum: float | None = Field(default=None, ge=0)
    maximum: float | None = Field(default=None, ge=0)
    currency_code: str = Field(default="USD", min_length=3, max_length=3)

    @model_validator(mode="after")
    def validate_range(self) -> "ClarificationBudgetRange":
        if (
            self.minimum is not None
            and self.maximum is not None
            and self.maximum < self.minimum
        ):
            raise ValueError("Maximum budget must not be lower than minimum budget.")
        return self


class ClarificationSlotState(BaseModel):
    slot: ClarificationSlot
    value_label: str | None = Field(default=None, max_length=160)
    confidence: float = Field(default=1.0, ge=0, le=1)
    ambiguous: bool = False
    explicit_unknown: bool = False
    source: Literal["user", "extracted", "system"] = "extracted"


class ClarificationQuestion(BaseModel):
    slot: ClarificationSlot
    prompt: str = Field(min_length=1, max_length=240)
    helper_text: str | None = Field(default=None, max_length=240)


class ClarificationRecapChip(BaseModel):
    slot: ClarificationSlot
    label: str = Field(min_length=1, max_length=60)
    value_label: str = Field(min_length=1, max_length=160)
    editable: bool = True
    explicit_unknown: bool = False


class ClarificationRecap(BaseModel):
    chips: list[ClarificationRecapChip] = Field(default_factory=list)
    continue_label: str = Field(default="Continue to Recommendations", max_length=80)


class ClarificationState(BaseModel):
    destination: ClarificationSlotState
    timeline: ClarificationSlotState
    trip_length: ClarificationSlotState
    budget: ClarificationSlotState
    next_question: ClarificationQuestion | None = None
    recap: ClarificationRecap = Field(default_factory=ClarificationRecap)
    all_critical_slots_resolved: bool = False


class ClarificationAnswer(BaseModel):
    slot: ClarificationSlot
    answer_text: str | None = Field(default=None, max_length=500)
    explicit_unknown: bool = False

    @model_validator(mode="after")
    def validate_answer(self) -> "ClarificationAnswer":
        if not self.explicit_unknown and not self.answer_text:
            raise ValueError("answer_text is required unless explicit_unknown is true.")
        return self


class ClarificationRecapEdit(BaseModel):
    slot: ClarificationSlot
    edited_value: str | None = Field(default=None, max_length=500)
    explicit_unknown: bool = False

    @model_validator(mode="after")
    def validate_edit(self) -> "ClarificationRecapEdit":
        if not self.explicit_unknown and not self.edited_value:
            raise ValueError("edited_value is required unless explicit_unknown is true.")
        return self


class ConstraintUpdates(BaseModel):
    destination: str | None = Field(default=None, max_length=120)
    date_range: SearchDateRange | None = None
    trip_length_days: int | None = Field(default=None, ge=1, le=60)
    budget_range: ClarificationBudgetRange | None = None
    explicit_unknown_slots: list[ClarificationSlot] = Field(default_factory=list)


class SearchRequest(BaseModel):
    query: str | None = Field(default=None, max_length=500)
    inventory: list[InventoryType] = Field(
        default_factory=lambda: [InventoryType.STAY, InventoryType.FLIGHT]
    )
    destination: str | None = Field(default=None, max_length=120)
    origin: str | None = Field(default=None, max_length=120)
    date_range: SearchDateRange | None = None
    travelers: TravelerCounts = Field(default_factory=TravelerCounts)
    stay_filters: StayFilters = Field(default_factory=StayFilters)
    flight_filters: FlightFilters = Field(default_factory=FlightFilters)
    currency_code: str = Field(default="USD", min_length=3, max_length=3)
    limit_per_provider: int = Field(default=5, ge=1, le=20)
    clarification_answer: ClarificationAnswer | None = None
    recap_edit: ClarificationRecapEdit | None = None
    constraint_updates: ConstraintUpdates | None = None

    @field_validator("inventory")
    @classmethod
    def dedupe_inventory(cls, value: list[InventoryType]) -> list[InventoryType]:
        unique = list(dict.fromkeys(value))
        if not unique:
            raise ValueError("At least one inventory type is required.")
        return unique

    @model_validator(mode="after")
    def validate_payload(self) -> "SearchRequest":
        has_clarification_update = any(
            [self.clarification_answer, self.recap_edit, self.constraint_updates]
        )
        if not self.query and not self.destination and not has_clarification_update:
            raise ValueError(
                "Either query or destination must be provided unless clarification updates are supplied."
            )
        return self


class AppliedFilters(BaseModel):
    destination: str | None = None
    origin: str | None = None
    date_range: SearchDateRange | None = None
    travelers: TravelerCounts
    stay_filters: StayFilters
    flight_filters: FlightFilters

    @classmethod
    def from_request(cls, request: SearchRequest) -> "AppliedFilters":
        return cls(
            destination=request.destination,
            origin=request.origin,
            date_range=request.date_range,
            travelers=request.travelers,
            stay_filters=request.stay_filters,
            flight_filters=request.flight_filters,
        )


class ProviderStatus(BaseModel):
    provider: str
    label: str
    configured: bool
    healthy: bool
    inventory_types: list[InventoryType]
    reason: str | None = None


class BaseSearchResult(BaseModel):
    provider: str
    provider_label: str
    title: str
    description: str
    total_price: float
    currency: str
    redirect_url: str | None = None
    deep_link_label: str | None = None
    score: float = 0.0
    price_known: bool = True
    price_label: str | None = None


class StaySearchResult(BaseSearchResult):
    inventory_type: Literal[InventoryType.STAY]
    location_label: str | None = None
    rating: str | None = None
    amenities: list[str] = Field(default_factory=list)
    nightly_price: float | None = None
    check_in: str | None = None
    check_out: str | None = None


class FlightSearchResult(BaseSearchResult):
    inventory_type: Literal[InventoryType.FLIGHT]
    origin_code: str
    destination_code: str
    departure_at: str
    arrival_at: str
    carrier_codes: list[str] = Field(default_factory=list)
    stops: int = 0
    duration: str | None = None


SearchResult = Annotated[
    Union[StaySearchResult, FlightSearchResult],
    Field(discriminator="inventory_type"),
]


class SearchResponse(BaseModel):
    search_id: str
    query: str
    requested_inventory: list[InventoryType]
    applied_filters: AppliedFilters
    provider_status: list[ProviderStatus]
    warnings: list[str] = Field(default_factory=list)
    results: list[SearchResult] = Field(default_factory=list)
    clarification_state: ClarificationState | None = None


class ProviderStatusResponse(BaseModel):
    providers: list[ProviderStatus]


class HealthResponse(BaseModel):
    status: str
    database: bool
    redis: bool
    providers: list[ProviderStatus]
    warnings: list[str] = Field(default_factory=list)
