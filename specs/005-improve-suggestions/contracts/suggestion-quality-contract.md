# Contract: Post-Intent Suggestion Quality

## Purpose

Define the behavioral contract for suggestion generation after intent capture and clarification updates.

## Inputs

The suggestion pipeline consumes:

- Current resolved intent profile
- Clarification answer or recap edit (if provided this turn)
- Existing session state from prior turns

## Required Behaviors

1. **Constraint Preservation**
   - Previously resolved critical slots remain applied in subsequent turns unless explicitly edited.

2. **Question Progression**
   - The system asks at most one follow-up question per turn.
   - Already resolved slots are not re-asked unless invalidated by a user edit.

3. **Suggestion Fit**
   - Suggestions are ranked after hard-constraint gating.
   - Suggestions violating hard constraints are labeled and deprioritized.

4. **Suggestion Diversity**
   - Near-duplicate suggestions are suppressed within the same response.

5. **Suggestion Transparency**
   - Each suggestion includes concise rationale linked to resolved constraints.

6. **Fallback Behavior**
   - If no high-fit suggestions exist, return partial-fit fallback suggestions with clear labels and rationale.

## Output Expectations

Each suggestion set must include:

- Ranked suggestion list
- Per-suggestion rationale
- Constraint status visibility
- Updated clarification/session state for next turn

## Non-Compliance Signals

The contract is considered violated if any of the following occur:

- A previously resolved slot is lost without user edit
- The same unresolved slot is repeatedly asked despite accepted valid answer
- Top suggestions conflict with hard constraints without explicit labeling
- Suggestion list contains semantic duplicates
- Suggestions are returned without rationale
