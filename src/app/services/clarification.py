from __future__ import annotations

from datetime import UTC, datetime

from src.app.schemas.search import (
    ClarificationHistoryEntry,
    ClarificationQuestion,
    ClarificationRecap,
    ClarificationRecapChip,
    ClarificationSlot,
    ClarificationSlotState,
    ClarificationState,
    DestinationSelectionMode,
    DestinationSuggestion,
    DestinationSuggestionKind,
    DestinationSuggestionSource,
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
    ClarificationSlot.TIMELINE: (ClarificationSlot.BUDGET,),
    ClarificationSlot.TRIP_LENGTH: (ClarificationSlot.BUDGET,),
    ClarificationSlot.BUDGET: (),
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

_REGION_SUGGESTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("North America", ("family-friendly", "easy-access")),
    ("Central America", ("warm", "beach")),
    ("Europe", ("culture", "walkable")),
    ("Caribbean", ("warm", "beach")),
    ("Asia-Pacific", ("beach", "adventure")),
)

_CURATED_DESTINATIONS: tuple[tuple[str, str, tuple[str, ...], float], ...] = (
    ("cancun-mx", "Cancun", ("warm", "beach", "family-friendly"), 0.92),
    ("punta-cana-do", "Punta Cana", ("warm", "beach", "all-inclusive"), 0.9),
    ("maui-us", "Maui", ("warm", "beach", "romantic"), 0.88),
    ("mallorca-es", "Mallorca", ("warm", "beach", "culture"), 0.86),
    ("algarve-pt", "Algarve", ("warm", "beach", "relaxed"), 0.84),
)


def slot_requires_follow_up(slot_state: ClarificationSlotState) -> bool:
    if slot_state.explicit_unknown:
        return False
    if not slot_state.value_label:
        return True
    return slot_state.ambiguous


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


def build_destination_suggestions(
    *,
    destination_state: ClarificationSlotState,
    query_text: str | None,
    selected_candidates: list[str] | None = None,
) -> list[DestinationSuggestion]:
    if not slot_requires_follow_up(destination_state):
        return []

    selected = {candidate.strip().lower() for candidate in selected_candidates or [] if candidate.strip()}
    query_signals = _extract_query_signals(query_text)

    suggestions: list[DestinationSuggestion] = [
        DestinationSuggestion(
            id=f"region:{label.lower().replace(' ', '-')}",
            kind=DestinationSuggestionKind.REGION,
            label=label,
            signals=list(signals),
            source=DestinationSuggestionSource.CURATED,
            popularity_score=0.75,
        )
        for label, signals in _REGION_SUGGESTIONS
    ]

    for destination_id, label, signals, popularity_score in _CURATED_DESTINATIONS:
        if label.lower() in selected:
            continue
        if query_signals and query_signals.isdisjoint(set(signals)):
            continue
        suggestions.append(
            DestinationSuggestion(
                id=f"destination:{destination_id}",
                kind=DestinationSuggestionKind.DESTINATION,
                label=label,
                signals=list(signals),
                source=DestinationSuggestionSource.TREND,
                popularity_score=popularity_score,
            )
        )
    return suggestions


def resolve_destination_selection_mode(
    explicit_mode: DestinationSelectionMode | None,
    destination_candidates: list[str],
    destination: str | None,
) -> DestinationSelectionMode:
    if explicit_mode is not None:
        return explicit_mode
    if len(destination_candidates) > 1:
        return DestinationSelectionMode.COMPARE
    return DestinationSelectionMode.SINGLE


def normalize_destination_candidates(
    *,
    destination_candidates: list[str] | None,
    destination: str | None,
) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []

    for raw_value in [*(destination_candidates or []), destination]:
        if not raw_value:
            continue
        value = raw_value.strip()
        if not value:
            continue
        dedupe_key = value.lower()
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(value)
    return normalized


def _extract_query_signals(query_text: str | None) -> set[str]:
    if not query_text:
        return set()
    lowered = query_text.lower()
    keywords = {
        "warm": "warm",
        "beach": "beach",
        "family": "family-friendly",
        "romantic": "romantic",
        "adventure": "adventure",
        "culture": "culture",
    }
    return {signal for token, signal in keywords.items() if token in lowered}


def build_clarification_state(
    slot_states: dict[ClarificationSlot, ClarificationSlotState],
    history: list[ClarificationHistoryEntry] | None = None,
    weather_state: ClarificationSlotState | None = None,
) -> ClarificationState:
    resolved = all_critical_slots_resolved(slot_states)
    next_question = None if resolved else select_next_question(slot_states)
    return ClarificationState(
        destination=slot_states[ClarificationSlot.DESTINATION],
        timeline=slot_states[ClarificationSlot.TIMELINE],
        trip_length=slot_states[ClarificationSlot.TRIP_LENGTH],
        budget=slot_states[ClarificationSlot.BUDGET],
        weather=weather_state,
        next_question=next_question,
        recap=build_recap(slot_states),
        all_critical_slots_resolved=resolved,
        history=history or [],
    )


def slot_state_from_metadata(
    slot: ClarificationSlot,
    metadata: dict | None,
) -> ClarificationSlotState:
    metadata = metadata or {}
    value = metadata.get("value")
    value_label = None if value is None else str(value)
    if isinstance(value, dict):
        value_label = metadata.get("source_text") or str(value)
    return ClarificationSlotState(
        slot=slot,
        value_label=value_label,
        normalized_value=value if isinstance(value, dict) else None,
        confidence=float(metadata.get("confidence", 0.0)),
        ambiguous=bool(metadata.get("ambiguous", value is None)),
        source_text=metadata.get("source_text"),
        source="extracted",
    )


def make_history_entry(
    *,
    slot: ClarificationSlot,
    previous_value: str | None,
    new_value: str | None,
    action: str,
) -> ClarificationHistoryEntry:
    return ClarificationHistoryEntry(
        timestamp=datetime.now(UTC),
        slot=slot,
        previous_value=previous_value,
        new_value=new_value,
        action=action,
    )


def reopen_related_slots(
    slot_states: dict[ClarificationSlot, ClarificationSlotState],
    edited_slot: ClarificationSlot,
) -> None:
    for related_slot in RELATED_SLOT_GRAPH.get(edited_slot, ()):
        state = slot_states[related_slot]
        slot_states[related_slot] = state.model_copy(
            update={
                "ambiguous": True,
                "confidence": min(state.confidence, GLOBAL_CONFIDENCE_THRESHOLD - 0.01),
            }
        )
