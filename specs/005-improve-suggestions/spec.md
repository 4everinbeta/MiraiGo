# Feature Specification: Improve Post-Intent Suggestions

**Feature Branch**: `005-improve-suggestions`

**Created**: 2026-05-18

**Status**: Draft

**Input**: User description: "improve the suggestions made after intent is defined"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - More Relevant Suggestions (Priority: P1)

After a traveler finishes sharing intent details, they receive destination and travel-option suggestions that clearly match their stated constraints (destination style, budget level, timeline, and trip length) instead of generic or weakly related options.

**Why this priority**: Relevance is the core value of the product. If suggestions do not match intent, users lose trust and abandon the flow.

**Independent Test**: Submit a fully specified intent and verify the top suggestions directly align with all required constraints and include an explanation of that alignment.

**Acceptance Scenarios**:

1. **Given** a fully defined intent with destination style, timeline, trip length, and budget, **When** suggestions are generated, **Then** the top suggestions satisfy the stated constraints and are not contradicted by the recap.
2. **Given** a user intent that includes strict budget constraints, **When** suggestions are generated, **Then** the list prioritizes options within budget and clearly labels over-budget alternatives.
3. **Given** a user intent that includes preferred trip style (for example beach or mountains), **When** suggestions are generated, **Then** the suggested options reflect that style and include rationale tied to user input.

---

### User Story 2 - Stable Multi-Turn Suggestion Quality (Priority: P1)

As users answer follow-up questions, the system keeps previously resolved intent values and improves suggestions incrementally rather than losing known constraints or repeatedly asking the same slot.

**Why this priority**: Multi-turn stability prevents frustration and ensures the system can complete the journey from unclear prompt to actionable recommendations.

**Independent Test**: Start with a partial prompt, answer follow-up questions across multiple turns, and verify previously answered constraints remain preserved while suggestion quality improves each turn.

**Acceptance Scenarios**:

1. **Given** a partial prompt with missing timeline or budget, **When** the user answers a follow-up question, **Then** prior resolved constraints remain intact in recap and are still applied to suggestions.
2. **Given** a resolved slot from a previous turn, **When** a later turn is submitted without changing that slot, **Then** the system does not re-ask that same question unless the user explicitly edits it.
3. **Given** multiple follow-up turns, **When** suggestions are refreshed, **Then** the list reflects cumulative known intent rather than resetting to generic defaults.

---

### User Story 3 - Actionable Suggestion Transparency (Priority: P2)

Users can understand why each suggestion was shown and quickly adjust constraints when results are close but not ideal.

**Why this priority**: Transparent rationale helps users trust results and self-correct constraints without leaving the flow.

**Independent Test**: Generate suggestions and confirm each recommendation includes concise reason signals and supports immediate constraint edits that update the next suggestion set.

**Acceptance Scenarios**:

1. **Given** a set of suggestions, **When** the user reviews them, **Then** each suggestion displays a brief explanation tied to one or more stated constraints.
2. **Given** a user edits a recap chip (for example timeline or budget), **When** they submit the edit, **Then** refreshed suggestions reflect the new value and no stale explanation remains.

---

### Edge Cases

- What happens when all available suggestions conflict with at least one hard user constraint?
- How does the system respond when user answers are valid but low-specificity (for example "summer" or "moderate budget")?
- What happens when multiple suggestions are effectively duplicates with only minor differences?
- How does the system behave when user-provided constraints are internally inconsistent (for example ultra-low budget with premium-only expectations)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate suggestions only after applying the current resolved intent profile (destination preference, timeline, trip length, and budget state).
- **FR-002**: System MUST preserve previously resolved intent constraints across follow-up turns unless explicitly changed by the user.
- **FR-003**: System MUST avoid re-asking already resolved critical slots unless a direct user edit invalidates that slot.
- **FR-004**: System MUST rank suggestions by intent fit and prioritize suggestions that satisfy explicit user constraints.
- **FR-005**: System MUST mark suggestions that violate hard constraints and explain why they are still shown.
- **FR-006**: System MUST include a concise rationale for each suggestion, referencing at least one resolved user constraint.
- **FR-007**: System MUST refresh suggestions after accepted follow-up answers or recap edits using the updated constraint set.
- **FR-008**: System MUST avoid near-duplicate suggestions in the same response set by enforcing meaningful differentiation.
- **FR-009**: System MUST provide a graceful fallback when no high-fit suggestions exist, while keeping user constraints visible and editable.

### Key Entities *(include if feature involves data)*

- **Intent Profile**: The current set of resolved and unresolved user constraints that drives suggestion generation.
- **Suggestion Candidate**: A generated option with fit signals, constraint match state, and user-facing rationale.
- **Suggestion Session State**: Turn-by-turn context that preserves answered slots, user edits, and active clarification progress.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90% of fully specified intent submissions return suggestion sets where the top 3 options satisfy all explicit hard constraints.
- **SC-002**: In multi-turn journeys, repeated questions for already resolved critical slots occur in fewer than 2% of sessions unless users explicitly edit those slots.
- **SC-003**: At least 95% of suggestion responses include a user-visible rationale for every displayed suggestion.
- **SC-004**: At least 85% of users can reach a suggestion set they consider usable within two clarification turns after the initial prompt.
- **SC-005**: Duplicate or near-duplicate suggestions account for fewer than 5% of displayed suggestion sets.

## Assumptions

- Users continue to interact through the existing natural-language-first prompt and follow-up workflow.
- Existing recap editing remains the primary mechanism for users to correct constraints mid-session.
- Suggestion quality improvement for this feature is focused on relevance, stability, and explanation quality rather than adding new booking capabilities.
- The feature targets current web users first; no separate mobile-only interaction model is required for initial rollout.
- Existing destination and budget taxonomies are sufficient for v1 of this improvement and can be refined in later iterations.
