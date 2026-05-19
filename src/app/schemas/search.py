from __future__ import annotations

from datetime import UTC, date, datetime
from enum import Enum
from typing import Annotated, Any, Literal, Union

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
    WEATHER = "weather"


class DestinationSuggestionKind(str, Enum):
    REGION = "region"
    DESTINATION = "destination"


class DestinationSuggestionSource(str, Enum):
    CURATED = "curated"
    TREND = "trend"
    EXTRACTED = "extracted"


class DateFlexibility(str, Enum):
    FIXED = "fixed"
    FEW_DAYS = "few-days"
    WEEK_FLEX = "week-flex"
    FULLY_FLEXIBLE = "fully-flexible"


class DestinationSelectionMode(str, Enum):
    SINGLE = "single"
    COMPARE = "compare"


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
    normalized_value: dict[str, Any] | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    ambiguous: bool = False
    explicit_unknown: bool = False
    source_text: str | None = Field(default=None, max_length=240)
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
    weather: ClarificationSlotState | None = None
    destination_suggestions: list[DestinationSuggestion] = Field(default_factory=list)
    supports_multi_destination_compare: bool = False
    destination_selection_mode: DestinationSelectionMode | None = None
    resolved_destination_candidates: list[str] = Field(default_factory=list)
    next_question: ClarificationQuestion | None = None
    recap: ClarificationRecap = Field(default_factory=ClarificationRecap)
    all_critical_slots_resolved: bool = False
    history: list["ClarificationHistoryEntry"] = Field(default_factory=list)
    loop_guard_counter: int = Field(default=0, ge=0)
    repeated_question_slot: ClarificationSlot | None = None


class ClarificationHistoryEntry(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    slot: ClarificationSlot
    previous_value: str | None = Field(default=None, max_length=240)
    new_value: str | None = Field(default=None, max_length=240)
    action: Literal["answer", "recap_edit", "constraint_update", "extraction", "unknown"]


class WeatherPreference(BaseModel):
    temperature: Literal["warm", "cool", "pleasant"] | None = None
    precipitation: Literal["avoid_rain", "rain_ok"] | None = None
    source_text: str | None = Field(default=None, max_length=240)


class FlightPreferenceConstraints(BaseModel):
    nonstop: bool | None = None
    max_travel_hours: float | None = Field(default=None, gt=0, le=48)


class DestinationSuggestion(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    kind: DestinationSuggestionKind
    label: str = Field(min_length=1, max_length=120)
    parent_region: str | None = Field(default=None, max_length=120)
    signals: list[str] = Field(default_factory=list)
    popularity_score: float | None = Field(default=None, ge=0)
    source: DestinationSuggestionSource = DestinationSuggestionSource.CURATED


class RecommendationComparison(BaseModel):
    travel_time_fit: float | None = Field(default=None, ge=0, le=1)
    budget_fit: float | None = Field(default=None, ge=0, le=1)
    style_fit: float | None = Field(default=None, ge=0, le=1)
    flexibility_fit: float | None = Field(default=None, ge=0, le=1)


class RecommendationPackage(BaseModel):
    bundle_id: str = Field(min_length=1, max_length=120)
    destination: str = Field(min_length=1, max_length=120)
    score: float = 0.0
    rationale: list[str] = Field(default_factory=list)
    rationale_text: str | None = Field(default=None, max_length=280)
    reason_tags: list[str] = Field(default_factory=list)
    estimated_total_cost: float | None = Field(default=None, ge=0)
    hard_constraint_status: dict[str, bool] = Field(default_factory=dict)
    fallback_level: Literal["high-fit", "partial-fit", "fallback"] = "high-fit"
    duplicate_signature: str | None = Field(default=None, max_length=240)
    comparison: RecommendationComparison | None = None


class FlightOptionsGroup(BaseModel):
    primary: list[SearchResult] = Field(default_factory=list)
    nearby_date_alternatives: list[SearchResult] = Field(default_factory=list)
    partial_availability: bool = False
    warnings: list[str] = Field(default_factory=list)


class LodgingOptionsGroup(BaseModel):
    hotels: list[StaySearchResult] = Field(default_factory=list)
    bed_and_breakfasts: list[StaySearchResult] = Field(default_factory=list)
    vacation_rentals: list[StaySearchResult] = Field(default_factory=list)
    partial_availability: bool = False
    warnings: list[str] = Field(default_factory=list)


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
    destination_candidates: list[str] = Field(default_factory=list)
    destination_selection_mode: DestinationSelectionMode | None = None
    date_range: SearchDateRange | None = None
    trip_length_days: int | None = Field(default=None, ge=1, le=60)
    budget_range: ClarificationBudgetRange | None = None
    date_flexibility: DateFlexibility | None = None
    flight_preferences: FlightPreferenceConstraints | None = None
    trip_style_tags: list[str] = Field(default_factory=list)
    weather_preference: WeatherPreference | None = None
    explicit_unknown_slots: list[ClarificationSlot] = Field(default_factory=list)


class SearchRequest(BaseModel):
    query: str | None = Field(default=None, max_length=500)
    inventory: list[InventoryType] = Field(
        default_factory=lambda: [InventoryType.STAY, InventoryType.FLIGHT]
    )
    destination: str | None = Field(default=None, max_length=120)
    origin: str | None = Field(default=None, max_length=120)
    date_range: SearchDateRange | None = None
    trip_length_days: int | None = Field(default=None, ge=1, le=60)
    budget_range: ClarificationBudgetRange | None = None
    date_flexibility: DateFlexibility | None = None
    flight_preferences: FlightPreferenceConstraints | None = None
    trip_style_tags: list[str] = Field(default_factory=list)
    destination_candidates: list[str] = Field(default_factory=list)
    destination_selection_mode: DestinationSelectionMode | None = None
    weather_preference: WeatherPreference | None = None
    travelers: TravelerCounts = Field(default_factory=TravelerCounts)
    stay_filters: StayFilters = Field(default_factory=StayFilters)
    flight_filters: FlightFilters = Field(default_factory=FlightFilters)
    currency_code: str = Field(default="USD", min_length=3, max_length=3)
    limit_per_provider: int = Field(default=5, ge=1, le=20)
    clarification_answer: ClarificationAnswer | None = None
    recap_edit: ClarificationRecapEdit | None = None
    constraint_updates: ConstraintUpdates | None = None
    clarification_state: ClarificationState | None = None

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
    destination_candidates: list[str] = Field(default_factory=list)
    destination_selection_mode: DestinationSelectionMode | None = None
    origin: str | None = None
    date_range: SearchDateRange | None = None
    trip_length_days: int | None = None
    budget_range: ClarificationBudgetRange | None = None
    date_flexibility: DateFlexibility | None = None
    flight_preferences: FlightPreferenceConstraints | None = None
    trip_style_tags: list[str] = Field(default_factory=list)
    weather_preference: WeatherPreference | None = None
    travelers: TravelerCounts
    stay_filters: StayFilters
    flight_filters: FlightFilters

    @classmethod
    def from_request(cls, request: SearchRequest) -> "AppliedFilters":
        return cls(
            destination=request.destination,
            destination_candidates=request.destination_candidates,
            destination_selection_mode=request.destination_selection_mode,
            origin=request.origin,
            date_range=request.date_range,
            trip_length_days=request.trip_length_days,
            budget_range=request.budget_range,
            date_flexibility=request.date_flexibility,
            flight_preferences=request.flight_preferences,
            trip_style_tags=request.trip_style_tags,
            weather_preference=request.weather_preference,
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
    recommendation_packages: list[RecommendationPackage] = Field(default_factory=list)
    flight_options: FlightOptionsGroup | None = None
    lodging_options: LodgingOptionsGroup | None = None


class ProviderStatusResponse(BaseModel):
    providers: list[ProviderStatus]


class HealthResponse(BaseModel):
    status: str
    database: bool
    redis: bool
    providers: list[ProviderStatus]
    warnings: list[str] = Field(default_factory=list)
