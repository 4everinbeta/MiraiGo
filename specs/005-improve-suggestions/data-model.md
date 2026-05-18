# Data Model: Improve Post-Intent Suggestions

## IntentProfile

Represents the current resolved user intent at any turn.

| Field | Type | Description |
|------|------|-------------|
| destination | string \| null | Primary resolved destination intent if singular |
| destination_candidates | string[] | Candidate destinations when comparison mode is active |
| timeline_window | object \| null | Normalized travel window or season |
| trip_length_days | number \| null | Resolved duration in days |
| budget_range | object \| null | Normalized minimum/maximum budget |
| weather_preference | object \| null | Warm/cool/rain preference signal |
| style_tags | string[] | Travel-style intent tags (beach, mountain, etc.) |
| confidence_by_slot | map | Confidence values by critical slot |
| explicit_unknown_slots | string[] | Slots marked unknown by user |

### Validation Rules

- A slot marked explicit unknown must not block forward progress.
- Resolved slots remain stable across turns unless explicitly edited.
- Low-confidence slot values are eligible for clarification prompts.

---

## SuggestionCandidate

Represents one post-intent recommendation option.

| Field | Type | Description |
|------|------|-------------|
| id | string | Stable identifier for display and selection |
| title | string | User-facing suggestion label |
| destination_key | string | Canonical destination reference |
| fit_score | number | Composite fit score (post hard-constraint gate) |
| hard_constraint_status | object | Per-constraint pass/fail state |
| fallback_level | string | `high-fit`, `partial-fit`, or `fallback` |
| rationale_tags | string[] | Compact reason labels tied to intent |
| rationale_text | string | Plain-language why-this-was-suggested sentence |
| duplicate_signature | string | Semantic signature for dedup suppression |

### Validation Rules

- Each candidate must include at least one rationale tag.
- Candidates failing hard constraints must be marked and deprioritized.
- Duplicate signatures must not appear more than once in final list.

---

## SuggestionSessionState

Tracks turn-by-turn suggestion and clarification continuity.

| Field | Type | Description |
|------|------|-------------|
| session_id | string | Session identifier |
| intent_profile | IntentProfile | Current resolved constraints |
| clarification_state | object | Current question, recap chips, and slot states |
| previous_suggestion_ids | string[] | Last turn suggestion IDs |
| iteration_count | number | Turn count for guardrails and analytics |
| loop_guard_counter | number | Repeated-question protection counter |

### State Transitions

1. **Initial prompt submitted** → partial IntentProfile + clarification decision
2. **Clarification answer accepted** → IntentProfile enriched, session state updated
3. **Suggestion generation** → candidate set ranked, deduped, and explained
4. **Recap edit submitted** → affected slots reopened, profile updated, suggestions regenerated
5. **Completion** → all critical slots resolved or explicitly unknown, stable suggestion set returned
