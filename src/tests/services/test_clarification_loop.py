from src.app.schemas.search import ClarificationSlot, ClarificationSlotState
from src.app.services.clarification import (
    CRITICAL_SLOT_ORDER,
    GLOBAL_CONFIDENCE_THRESHOLD,
    build_clarification_state,
    select_next_question,
)


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
