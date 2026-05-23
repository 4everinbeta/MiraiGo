from src.app.schemas.search import (
    ClarificationBudgetRange,
    ClarificationSlot,
    ClarificationSlotState,
    SearchRequest,
    WeatherPreference,
)
from src.app.services.clarification import (
    CRITICAL_SLOT_ORDER,
    FLIGHT_PREREQUISITE_FIELDS,
    GLOBAL_CONFIDENCE_THRESHOLD,
    build_clarification_state,
    get_missing_flight_prerequisites,
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


def test_timeline_with_value_does_not_reask_only_for_low_confidence():
    slot_states = {
        ClarificationSlot.DESTINATION: _slot_state(ClarificationSlot.DESTINATION, "Lisbon"),
        ClarificationSlot.TIMELINE: ClarificationSlotState(
            slot=ClarificationSlot.TIMELINE,
            value_label="June",
            confidence=0.5,
            ambiguous=False,
            explicit_unknown=False,
            source="extracted",
        ),
        ClarificationSlot.TRIP_LENGTH: _slot_state(ClarificationSlot.TRIP_LENGTH, None),
        ClarificationSlot.BUDGET: _slot_state(ClarificationSlot.BUDGET, None),
    }

    next_question = select_next_question(slot_states)
    assert next_question is not None
    assert next_question.slot == ClarificationSlot.TRIP_LENGTH


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
    # INTENT-03: ask one focused clarification at a time in strict priority order.
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
    # INTENT-04: continue path must preserve resolved critical slots.
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


def test_extract_origin_hint_stops_before_trailing_context():
    service = SearchService()
    assert service._extract_origin_hint("Trip to Barcelona from Denver for two adults") == "Denver"
    assert service._extract_origin_hint("From JFK to Lisbon in June") == "JFK"


def test_uncertain_prompt_keeps_destination_as_first_clarification_slot():
    service = SearchService()
    request = SearchRequest(query="Maybe somewhere warm in early summer")

    _, _, state = service._resolve_request(request)

    assert state.next_question is not None
    assert state.next_question.slot == ClarificationSlot.DESTINATION


def test_timeline_recap_edit_keeps_trip_length_resolved():
    service = SearchService()
    request = SearchRequest(
        query="Trip to Lisbon in early summer",
        destination="Lisbon",
        date_range={"start": "2026-06-01", "end": "2026-06-10"},
        trip_length_days=7,
        budget_range=ClarificationBudgetRange(minimum=1500, maximum=2500, currency_code="USD"),
        recap_edit={
            "slot": ClarificationSlot.TIMELINE,
            "edited_value": "late June",
            "explicit_unknown": False,
        },
    )

    _, _, state = service._resolve_request(request)

    assert state.trip_length.value_label is not None
    assert state.trip_length.ambiguous is False
    assert state.next_question is None or state.next_question.slot != ClarificationSlot.DESTINATION


def test_budget_recap_edit_does_not_reopen_destination():
    service = SearchService()
    request = SearchRequest(
        query="Trip to Lisbon in June",
        destination="Lisbon",
        date_range={"start": "2026-06-01", "end": "2026-06-10"},
        trip_length_days=7,
        budget_range=ClarificationBudgetRange(minimum=1500, maximum=2500, currency_code="USD"),
        recap_edit={
            "slot": ClarificationSlot.BUDGET,
            "edited_value": "$1800-$2600",
            "explicit_unknown": False,
        },
    )

    _, _, state = service._resolve_request(request)

    assert state.destination.value_label == "Lisbon"
    assert state.next_question is None


def test_early_summer_timeline_does_not_reask_timeline_when_destination_present():
    service = SearchService()
    request = SearchRequest(query="Trip to Lisbon in early summer")

    _, _, state = service._resolve_request(request)

    assert state.destination.value_label == "Lisbon"
    assert state.timeline.value_label is not None
    assert state.next_question is not None
    assert state.next_question.slot == ClarificationSlot.TRIP_LENGTH


def test_timeline_follow_up_accepts_season_answer_without_looping():
    service = SearchService()
    first_turn = SearchRequest(query="Trip to Lisbon on a moderate budget")

    _, _, state = service._resolve_request(first_turn)
    assert state.next_question is not None
    assert state.next_question.slot == ClarificationSlot.TIMELINE

    second_turn = first_turn.model_copy(
        update={
            "clarification_answer": {
                "slot": ClarificationSlot.TIMELINE,
                "answer_text": "this summer",
                "explicit_unknown": False,
            }
        }
    )
    resolved, _, state = service._resolve_request(second_turn)
    assert resolved.date_range is not None
    assert state.next_question is not None
    assert state.next_question.slot == ClarificationSlot.TRIP_LENGTH


def test_budget_follow_up_accepts_qualitative_budget_answer():
    service = SearchService()
    first_turn = SearchRequest(query="Trip to Lisbon in June for 7 days")

    _, _, state = service._resolve_request(first_turn)
    assert state.next_question is not None
    assert state.next_question.slot == ClarificationSlot.BUDGET

    second_turn = first_turn.model_copy(
        update={
            "clarification_answer": {
                "slot": ClarificationSlot.BUDGET,
                "answer_text": "moderate budget",
                "explicit_unknown": False,
            }
        }
    )
    resolved, _, state = service._resolve_request(second_turn)
    assert resolved.budget_range is not None
    assert resolved.budget_range.maximum is not None
    assert state.next_question is None


def test_repeated_question_guard_advances_after_same_slot_repeats():
    service = SearchService()
    first_turn = SearchRequest(query="Trip ideas")
    _, _, first_state = service._resolve_request(first_turn)
    assert first_state.next_question is not None
    assert first_state.next_question.slot == ClarificationSlot.DESTINATION

    second_turn = first_turn.model_copy(update={"clarification_state": first_state})
    _, _, second_state = service._resolve_request(second_turn)
    assert second_state.next_question is not None
    assert second_state.next_question.slot == ClarificationSlot.DESTINATION
    assert second_state.loop_guard_counter == 1

    third_turn = second_turn.model_copy(
        update={
            "clarification_state": second_state,
            "clarification_answer": {
                "slot": ClarificationSlot.DESTINATION,
                "answer_text": "Lisbon",
                "explicit_unknown": False,
            },
        }
    )
    _, _, third_state = service._resolve_request(third_turn)
    assert third_state.next_question is not None
    assert third_state.next_question.slot == ClarificationSlot.TIMELINE


def test_clarification_state_surfaces_unresolved_flight_requirements_when_slots_are_resolved():
    slot_states = {
        ClarificationSlot.DESTINATION: _slot_state(ClarificationSlot.DESTINATION, "Lisbon"),
        ClarificationSlot.TIMELINE: _slot_state(ClarificationSlot.TIMELINE, "June"),
        ClarificationSlot.TRIP_LENGTH: _slot_state(ClarificationSlot.TRIP_LENGTH, "7 days"),
        ClarificationSlot.BUDGET: _slot_state(ClarificationSlot.BUDGET, "$2000"),
    }

    state = build_clarification_state(
        slot_states,
        flight_requirements_pending=["origin", "date_range"],
        continue_block_reason="Continue needs origin and date_range before flight recommendations can load.",
    )

    assert state.all_critical_slots_resolved is True
    assert state.flight_requirements_pending == ["origin", "date_range"]
    assert state.continue_block_reason is not None


def test_search_gate_uses_shared_flight_prerequisite_contract():
    service = SearchService()
    request = SearchRequest(
        query="Lisbon in June for 7 days under $2,500",
        destination="Lisbon",
        date_range={"start": "2026-06-01", "end": "2026-06-08"},
        trip_length_days=7,
        budget_range=ClarificationBudgetRange(
            minimum=1500,
            maximum=2500,
            currency_code="USD",
        ),
    )

    resolved, _, clarification_state = service._resolve_request(request)
    can_show_flights, _ = service._can_show_flights(resolved)

    assert FLIGHT_PREREQUISITE_FIELDS == ("origin", "destination", "date_range")
    assert get_missing_flight_prerequisites(resolved) == clarification_state.flight_requirements_pending
    assert can_show_flights is False


def test_constraint_updates_origin_unblocks_flight_prerequisites():
    service = SearchService()
    blocked_request = SearchRequest(
        query="Lisbon trip in June for 7 days under $2,500",
        destination="Lisbon",
        date_range={"start": "2026-06-01", "end": "2026-06-08"},
        trip_length_days=7,
        budget_range=ClarificationBudgetRange(
            minimum=1500,
            maximum=2500,
            currency_code="USD",
        ),
        inventory=["flight"],
    )

    _, _, blocked_state = service._resolve_request(blocked_request)
    assert blocked_state.flight_requirements_pending == ["origin"]

    follow_up_request = blocked_request.model_copy(
        update={
            "clarification_state": blocked_state,
            "constraint_updates": {"origin": "Denver"},
        }
    )
    resolved_follow_up, _, follow_up_state = service._resolve_request(follow_up_request)

    assert resolved_follow_up.origin == "Denver"
    assert follow_up_state.flight_requirements_pending == []
    assert follow_up_state.continue_block_reason is None
