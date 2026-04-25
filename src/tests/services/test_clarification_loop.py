from src.app.schemas.search import (
    ClarificationBudgetRange,
    ClarificationSlot,
    ClarificationSlotState,
    SearchRequest,
    WeatherPreference,
)
from src.app.services.clarification import (
    CRITICAL_SLOT_ORDER,
    GLOBAL_CONFIDENCE_THRESHOLD,
    build_clarification_state,
    select_next_question,
)
from src.app.services.search import SearchService


def _slot_state(slot: ClarificationSlot, value: str | None, *, unknown: bool = False) -> ClarificationSlotState:
    return ClarificationSlotState(
        slot=slot,
        value_label=value,
        confidence=1.0 if value or unknown else 0.1,
        ambiguous=False,
        explicit_unknown=unknown,
        source="extracted",
    )


def test_critical_slot_order_matches_decision_priority():
    assert CRITICAL_SLOT_ORDER == (
        ClarificationSlot.DESTINATION,
        ClarificationSlot.TIMELINE,
        ClarificationSlot.TRIP_LENGTH,
        ClarificationSlot.BUDGET,
    )


def test_global_confidence_threshold_is_bounded():
    assert 0 < GLOBAL_CONFIDENCE_THRESHOLD < 1


def test_select_next_question_asks_first_missing_slot_only():
    slot_states = {
        ClarificationSlot.DESTINATION: _slot_state(ClarificationSlot.DESTINATION, None),
        ClarificationSlot.TIMELINE: _slot_state(ClarificationSlot.TIMELINE, None),
        ClarificationSlot.TRIP_LENGTH: _slot_state(ClarificationSlot.TRIP_LENGTH, "7 days"),
        ClarificationSlot.BUDGET: _slot_state(ClarificationSlot.BUDGET, None),
    }

    next_question = select_next_question(slot_states)
    assert next_question is not None
    assert next_question.slot == ClarificationSlot.DESTINATION


def test_build_clarification_state_has_no_next_question_when_resolved_or_unknown():
    slot_states = {
        ClarificationSlot.DESTINATION: _slot_state(ClarificationSlot.DESTINATION, "Lisbon"),
        ClarificationSlot.TIMELINE: _slot_state(ClarificationSlot.TIMELINE, "June"),
        ClarificationSlot.TRIP_LENGTH: _slot_state(ClarificationSlot.TRIP_LENGTH, None, unknown=True),
        ClarificationSlot.BUDGET: _slot_state(ClarificationSlot.BUDGET, "$2000"),
    }

    state = build_clarification_state(slot_states)
    assert state.all_critical_slots_resolved is True
    assert state.next_question is None


def test_missing_slots_are_asked_in_priority_order_one_by_one():
    service = SearchService()
    req = SearchRequest(query="Need a trip")

    _, _, state = service._resolve_request(req)
    assert state.next_question is not None
    assert state.next_question.slot == ClarificationSlot.DESTINATION

    req = req.model_copy(
        update={
            "clarification_answer": {
                "slot": ClarificationSlot.DESTINATION,
                "answer_text": "Lisbon",
                "explicit_unknown": False,
            }
        }
    )
    _, _, state = service._resolve_request(req)
    assert state.next_question is not None
    assert state.next_question.slot == ClarificationSlot.TIMELINE


def test_explicit_unknown_allows_progression_with_warning():
    service = SearchService()
    req = SearchRequest(query="Help me pick somewhere")
    _, _, state = service._resolve_request(req)
    assert state.next_question is not None

    req = req.model_copy(
        update={
            "clarification_answer": {
                "slot": ClarificationSlot.DESTINATION,
                "answer_text": None,
                "explicit_unknown": True,
            }
        }
    )
    _, warnings, state = service._resolve_request(req)
    assert state.destination.explicit_unknown is True
    assert any("broader options" in warning for warning in warnings)


def test_recap_edit_reopens_only_related_slots():
    service = SearchService()
    req = SearchRequest(
        query="Trip to Lisbon",
        destination="Lisbon",
        trip_length_days=7,
    )
    _, _, state = service._resolve_request(req)
    assert state.timeline.ambiguous is True

    req = req.model_copy(
        update={
            "recap_edit": {
                "slot": ClarificationSlot.DESTINATION,
                "edited_value": "Porto",
                "explicit_unknown": False,
            }
        }
    )
    _, _, state = service._resolve_request(req)
    assert state.timeline.ambiguous is True
    assert state.budget.ambiguous is True


def test_weather_state_is_carried_through_clarification():
    service = SearchService()
    req = SearchRequest(query="Find warm weather in July")
    _, _, state = service._resolve_request(req)

    assert state.weather is not None
    assert state.weather.source_text in {"warm weather", "warm"}
    assert state.weather.ambiguous is False


def test_continue_turn_with_preserved_resolved_fields_does_not_reopen_trip_length_or_budget():
    service = SearchService()

    first_turn = SearchRequest(
        query="Warm beach trip in June",
        destination="Honolulu",
        date_range={"start": "2026-06-10", "end": "2026-06-17"},
    )
    _, _, state = service._resolve_request(first_turn)
    assert state.next_question is not None
    assert state.next_question.slot == ClarificationSlot.TRIP_LENGTH

    second_turn = first_turn.model_copy(
        update={
            "trip_length_days": 7,
            "clarification_answer": {
                "slot": ClarificationSlot.TRIP_LENGTH,
                "answer_text": "7 days",
                "explicit_unknown": False,
            },
        }
    )
    _, _, state = service._resolve_request(second_turn)
    assert state.next_question is not None
    assert state.next_question.slot == ClarificationSlot.BUDGET

    third_turn = second_turn.model_copy(
        update={
            "budget_range": ClarificationBudgetRange(
                minimum=1500,
                maximum=2500,
                currency_code="USD",
            ),
            "clarification_answer": {
                "slot": ClarificationSlot.BUDGET,
                "answer_text": "$1500-$2500",
                "explicit_unknown": False,
            },
            "weather_preference": WeatherPreference(
                temperature="warm",
                precipitation="avoid_rain",
                source_text="warm and dry",
            ),
        }
    )
    _, _, state = service._resolve_request(third_turn)
    assert state.next_question is None
    assert state.all_critical_slots_resolved is True

    continue_turn = third_turn.model_copy(
        update={
            "clarification_answer": None,
            "recap_edit": None,
            "constraint_updates": None,
        }
    )
    resolved_continue, _, continue_state = service._resolve_request(continue_turn)

    assert resolved_continue.trip_length_days == 7
    assert resolved_continue.budget_range is not None
    assert resolved_continue.budget_range.minimum == 1500
    assert resolved_continue.budget_range.maximum == 2500
    assert resolved_continue.weather_preference is not None
    assert continue_state.next_question is None
    assert continue_state.trip_length.value_label is not None
    assert continue_state.budget.value_label is not None
    assert continue_state.all_critical_slots_resolved is True
