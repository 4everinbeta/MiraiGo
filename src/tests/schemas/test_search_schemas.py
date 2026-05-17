import pytest

from src.app.schemas.search import (
    ClarificationAnswer,
    ClarificationState,
    ClarificationSlot,
    DestinationSuggestion,
    DestinationSuggestionKind,
    DestinationSuggestionSource,
    FlightPreferenceConstraints,
    InventoryType,
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
