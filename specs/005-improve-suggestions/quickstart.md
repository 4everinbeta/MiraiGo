# Quickstart: Improve Post-Intent Suggestions

## Goal

Validate that post-intent suggestions are relevant, stable across turns, and transparently explained.

## Scenario 1: Fully specified intent returns high-fit suggestions

1. Submit:
   - "I want a warm beach trip in July for 7 days with a moderate budget."
2. Verify:
   - Suggestions align with beach + warm + July + moderate budget.
   - Any over-budget suggestion is clearly labeled.
   - Each suggestion includes rationale tied to constraints.

## Scenario 2: Multi-turn clarification preserves resolved constraints

1. Submit:
   - "I want a warm beach trip on a moderate budget."
2. Answer timeline follow-up:
   - "this summer"
3. Answer trip-length follow-up:
   - "7 days"
4. Verify:
   - Destination/style and budget remain preserved between turns.
   - Timeline question is not repeated after valid answer.
   - Suggestion quality improves as constraints are resolved.

## Scenario 3: Recap edit updates suggestions without stale state

1. Start from a resolved session.
2. Edit budget recap chip from moderate to luxury range.
3. Verify:
   - Suggestion set refreshes to match updated budget.
   - Old rationale tied to prior budget does not persist.
   - No duplicate suggestions appear in refreshed results.

## Scenario 4: Fallback path when no high-fit options exist

1. Submit intentionally restrictive constraints.
2. Verify:
   - System still returns fallback suggestions.
   - Fallback entries are labeled as partial fit.
   - User can continue by editing recap constraints.
