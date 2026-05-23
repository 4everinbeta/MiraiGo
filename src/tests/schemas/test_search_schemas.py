import pytest

from src.app.schemas.search import (
    AirfareFreshness,
    AirfareProvenance,
    ClarificationAnswer,
    ClarificationState,
    ClarificationSlot,
    DestinationSuggestion,
    DestinationSuggestionKind,
    DestinationSuggestionSource,
    FlightPreferenceConstraints,
    InventoryType,
    FlightSearchResult,
    SearchResponse,
    SearchDateRange,
    SearchRequest,
)


def test_search_request_defaults():
    payload = SearchRequest(query="Trip to Tokyo")
    assert payload.inventory == [InventoryType.STAY, InventoryType.FLIGHT]
    assert payload.travelers.adults == 1


def test_search_date_range_validation():
    with pytest.raises(ValueError):
        SearchDateRange(start="2026-05-08", end="2026-05-03")


def test_search_request_requires_query_or_destination():
    with pytest.raises(ValueError):
        SearchRequest(query=None, destination=None)


def test_search_request_allows_clarification_without_query_or_destination():
    payload = SearchRequest(
        query=None,
        destination=None,
        clarification_answer=ClarificationAnswer(
            slot=ClarificationSlot.DESTINATION,
            answer_text="Portugal",
        ),
    )
    assert payload.clarification_answer is not None


def test_search_request_accepts_additive_constraint_update_fields():
    payload = SearchRequest(
        query="Warm beach trip in July",
        destination_candidates=["Cancun", "Punta Cana"],
        destination_selection_mode="compare",
        date_flexibility="few-days",
        flight_preferences=FlightPreferenceConstraints(nonstop=True, max_travel_hours=6),
        trip_style_tags=["family-friendly", "relaxed"],
        constraint_updates={
            "destination_candidates": ["Cancun", "Punta Cana"],
            "destination_selection_mode": "compare",
            "date_flexibility": "few-days",
            "flight_preferences": {"nonstop": True, "max_travel_hours": 6},
            "trip_style_tags": ["family-friendly"],
        },
    )
    assert payload.destination_selection_mode == "compare"
    assert payload.destination_candidates == ["Cancun", "Punta Cana"]
    assert payload.date_flexibility == "few-days"
    assert payload.flight_preferences is not None
    assert payload.flight_preferences.nonstop is True
    assert payload.constraint_updates is not None
    assert payload.constraint_updates.destination_selection_mode == "compare"


def test_search_response_additive_fields_remain_optional_for_compatibility():
    response = SearchResponse(
        search_id="search-123",
        query="Trip request",
        requested_inventory=[InventoryType.STAY],
        applied_filters={
            "travelers": {"adults": 2, "children": 0, "infants": 0},
            "stay_filters": {"amenities": ["wifi"]},
            "flight_filters": {"nonstop": False},
        },
        provider_status=[],
        results=[],
    )
    assert response.clarification_state is None
    assert response.recommendation_packages == []
    assert response.flight_options is None
    assert response.lodging_options is None


def test_clarification_state_supports_destination_suggestion_payloads():
    state = ClarificationState.model_validate(
        {
            "destination": {
                "slot": "destination",
                "value_label": None,
                "confidence": 0,
                "ambiguous": True,
                "explicit_unknown": False,
                "source": "system",
            },
            "timeline": {
                "slot": "timeline",
                "value_label": "July",
                "confidence": 0.9,
                "ambiguous": False,
                "explicit_unknown": False,
                "source": "user",
            },
            "trip_length": {
                "slot": "trip_length",
                "value_label": "7 days",
                "confidence": 0.9,
                "ambiguous": False,
                "explicit_unknown": False,
                "source": "user",
            },
            "budget": {
                "slot": "budget",
                "value_label": "$3000",
                "confidence": 0.9,
                "ambiguous": False,
                "explicit_unknown": False,
                "source": "user",
            },
            "destination_suggestions": [
                DestinationSuggestion(
                    id="destination:cancun-mx",
                    kind=DestinationSuggestionKind.DESTINATION,
                    label="Cancun",
                    source=DestinationSuggestionSource.TREND,
                    popularity_score=0.92,
                ).model_dump(mode="json")
            ],
            "supports_multi_destination_compare": True,
            "destination_selection_mode": "compare",
            "resolved_destination_candidates": ["Cancun", "Punta Cana"],
            "recap": {"chips": [], "continue_label": "Continue to Recommendations"},
            "all_critical_slots_resolved": False,
            "history": [],
        }
    )
    assert state.destination_selection_mode == "compare"
    assert state.destination_suggestions[0].popularity_score == 0.92
    assert state.resolved_destination_candidates == ["Cancun", "Punta Cana"]


def test_flight_search_result_accepts_canonical_normalized_fields():
    flight = FlightSearchResult(
        inventory_type=InventoryType.FLIGHT,
        provider="amadeus",
        provider_label="Amadeus",
        title="MIA → CDG",
        description="Direct flight",
        total_price=1234.56,
        currency="USD",
        origin_code="MIA",
        destination_code="CDG",
        departure_at="2026-08-01T10:00:00Z",
        arrival_at="2026-08-01T18:00:00Z",
        carrier_codes=["AF"],
        price_minor=123456,
        currency_code="USD",
        duration_minutes=480,
        stops_count=0,
        normalized_offer_id="offer-abc",
        provider_offer_id="provider-123",
        missing_fields=[],
        conversion_status="native",
        airfare_provenance=AirfareProvenance(
            source_provider="amadeus",
            provider_offer_id="provider-123",
        ),
        airfare_freshness=AirfareFreshness(
            freshness_source="provider_quote",
            freshness_at="2026-08-01T09:55:00Z",
        ),
    )
    assert flight.price_minor == 123456
    assert flight.stops_count == 0
    assert flight.duration_minutes == 480


def test_flight_search_result_keeps_null_present_normalized_keys_with_missing_fields():
    flight = FlightSearchResult(
        inventory_type=InventoryType.FLIGHT,
        provider="duffel",
        provider_label="Duffel",
        title="SEA → LIS",
        description="Partial data",
        total_price=0.0,
        currency="USD",
        origin_code="SEA",
        destination_code="LIS",
        departure_at="2026-09-10T06:00:00Z",
        arrival_at="2026-09-10T16:00:00Z",
        price_minor=None,
        currency_code=None,
        duration_minutes=None,
        stops_count=None,
        normalized_offer_id=None,
        provider_offer_id=None,
        missing_fields=["duration_minutes", "price_minor", "stops_count"],
        conversion_status=None,
        airfare_provenance=AirfareProvenance(
            source_provider="duffel",
            provider_offer_id=None,
            source_quote_at=None,
            source_payload_ref=None,
        ),
        airfare_freshness=AirfareFreshness(
            freshness_source=None,
            freshness_at=None,
            fetched_at=None,
        ),
    )
    serialized = flight.model_dump()
    assert serialized["duration_minutes"] is None
    assert serialized["price_minor"] is None
    assert serialized["missing_fields"] == ["duration_minutes", "price_minor", "stops_count"]
    assert serialized["airfare_freshness"]["freshness_source"] is None


def test_flight_search_result_retains_deprecated_legacy_fields_for_phase_migration():
    assert "DEPRECATED" in (FlightSearchResult.model_fields["total_price"].description or "")
    assert "DEPRECATED" in (FlightSearchResult.model_fields["currency"].description or "")
    assert "DEPRECATED" in (FlightSearchResult.model_fields["stops"].description or "")
    assert "DEPRECATED" in (FlightSearchResult.model_fields["duration"].description or "")
