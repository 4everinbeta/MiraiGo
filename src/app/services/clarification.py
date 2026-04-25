from __future__ import annotations

from src.app.schemas.search import (
    ClarificationQuestion,
    ClarificationRecap,
    ClarificationRecapChip,
    ClarificationSlot,
    ClarificationSlotState,
    ClarificationState,
)

# Ordered list keeps one-question-at-a-time behavior deterministic (D-03/D-04).
CRITICAL_SLOT_ORDER: tuple[ClarificationSlot, ...] = (
    ClarificationSlot.DESTINATION,
    ClarificationSlot.TIMELINE,
    ClarificationSlot.TRIP_LENGTH,
    ClarificationSlot.BUDGET,
)

# Single v1 threshold keeps confidence policy predictable across slots (D-10).
GLOBAL_CONFIDENCE_THRESHOLD: float = 0.65

RELATED_SLOT_GRAPH: dict[ClarificationSlot, tuple[ClarificationSlot, ...]] = {
    ClarificationSlot.DESTINATION: (
        ClarificationSlot.TIMELINE,
        ClarificationSlot.BUDGET,
    ),
    ClarificationSlot.TIMELINE: (
        ClarificationSlot.TRIP_LENGTH,
        ClarificationSlot.BUDGET,
    ),
    ClarificationSlot.TRIP_LENGTH: (
        ClarificationSlot.TIMELINE,
        ClarificationSlot.BUDGET,
    ),
    ClarificationSlot.BUDGET: (
        ClarificationSlot.DESTINATION,
        ClarificationSlot.TIMELINE,
        ClarificationSlot.TRIP_LENGTH,
    ),
}

SLOT_PROMPTS: dict[ClarificationSlot, ClarificationQuestion] = {
    ClarificationSlot.DESTINATION: ClarificationQuestion(
        slot=ClarificationSlot.DESTINATION,
        prompt="Where do you want to travel?",
        helper_text="City, country, or broader region all work.",
    ),
    ClarificationSlot.TIMELINE: ClarificationQuestion(
        slot=ClarificationSlot.TIMELINE,
        prompt="When are you hoping to travel?",
        helper_text="Share a month, season, or date range.",
    ),
    ClarificationSlot.TRIP_LENGTH: ClarificationQuestion(
        slot=ClarificationSlot.TRIP_LENGTH,
        prompt="How long is your trip?",
        helper_text="A rough number of days is enough.",
    ),
    ClarificationSlot.BUDGET: ClarificationQuestion(
        slot=ClarificationSlot.BUDGET,
        prompt="What budget should we plan around?",
        helper_text="You can share a range or say you are unsure.",
    ),
}


def slot_requires_follow_up(slot_state: ClarificationSlotState) -> bool:
    if slot_state.explicit_unknown:
        return False
    if not slot_state.value_label:
        return True
    if slot_state.ambiguous:
        return True
    return slot_state.confidence < GLOBAL_CONFIDENCE_THRESHOLD


def all_critical_slots_resolved(slot_states: dict[ClarificationSlot, ClarificationSlotState]) -> bool:
    return all(not slot_requires_follow_up(slot_states[slot]) for slot in CRITICAL_SLOT_ORDER)


def select_next_question(
    slot_states: dict[ClarificationSlot, ClarificationSlotState],
) -> ClarificationQuestion | None:
    for slot in CRITICAL_SLOT_ORDER:
        if slot_requires_follow_up(slot_states[slot]):
            return SLOT_PROMPTS[slot]
    return None


def build_recap(slot_states: dict[ClarificationSlot, ClarificationSlotState]) -> ClarificationRecap:
    chips: list[ClarificationRecapChip] = []
    for slot in CRITICAL_SLOT_ORDER:
        state = slot_states[slot]
        value_label = (
            "I don't know"
            if state.explicit_unknown
            else (state.value_label or "Missing")
        )
        chips.append(
            ClarificationRecapChip(
                slot=slot,
                label=slot.value.replace("_", " ").title(),
                value_label=value_label,
                explicit_unknown=state.explicit_unknown,
            )
        )
    return ClarificationRecap(chips=chips)


def build_clarification_state(
    slot_states: dict[ClarificationSlot, ClarificationSlotState],
) -> ClarificationState:
    resolved = all_critical_slots_resolved(slot_states)
    next_question = None if resolved else select_next_question(slot_states)
    return ClarificationState(
        destination=slot_states[ClarificationSlot.DESTINATION],
        timeline=slot_states[ClarificationSlot.TIMELINE],
        trip_length=slot_states[ClarificationSlot.TRIP_LENGTH],
        budget=slot_states[ClarificationSlot.BUDGET],
        next_question=next_question,
        recap=build_recap(slot_states),
        all_critical_slots_resolved=resolved,
    )
