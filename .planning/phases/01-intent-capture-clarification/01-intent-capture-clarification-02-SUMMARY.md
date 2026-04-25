---
phase: 01-intent-capture-clarification
plan: 02
subsystem: api
tags: [fastapi, pydantic, nlp, clarification, testing]
requires:
  - phase: 01-intent-capture-clarification
    provides: clarification contract scaffolding and helper constants from plan 01
provides:
  - Confidence-aware intent extraction metadata for destination/timeline/trip-length/budget/weather slots
  - Iterative one-question clarification orchestration in SearchService with field-level merges
  - Explicit unknown + recap edit handling with append-only clarification history
  - API/schema propagation of weather clarification state across turns
affects: [search-service, search-api, intent-parser, clarification-loop]
tech-stack:
  added: []
  patterns:
    - global confidence threshold driven follow-up gating
    - one-question-at-a-time clarification with ordered critical slots
    - merge-only slot updates with explicit unknown progression
key-files:
  created: []
  modified:
    - src/app/nlp/intent.py
    - src/app/services/search.py
    - src/app/services/clarification.py
    - src/app/schemas/search.py
    - src/app/api/v1/search.py
    - src/tests/nlp/test_intent_confidence.py
    - src/tests/services/test_clarification_loop.py
    - src/tests/api/test_search.py
key-decisions:
  - "Use slot metadata `{value, confidence, ambiguous, source_text}` as canonical extraction output and derive compatibility fields from it."
  - "Short-circuit provider fan-out whenever clarification_state indicates unresolved critical slots."
  - "Restrict mergeable clarification updates to enum-backed critical slots to satisfy T-01-04 tampering mitigation."
patterns-established:
  - "Clarification state includes append-only per-turn history entries with slot/value transitions."
  - "Weather preference is preserved as normalized metadata in request filters and clarification payloads."
requirements-completed: [INTENT-01, INTENT-02, INTENT-03, INTENT-04]
duration: 7min
completed: 2026-04-25
---

# Phase 01 Plan 02: Intent Clarification Behavior Summary

**Implemented a confidence-aware NLP extraction and iterative backend clarification loop that preserves history, handles explicit unknowns, and carries weather constraints through API turns.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-25T00:27:34Z
- **Completed:** 2026-04-25T00:33:56Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- Added slot-level metadata (confidence/ambiguity/source text), normalized timeline and budget mappings, and weather normalization in `extract_intent`.
- Refactored `SearchService` resolution into a clarification-aware pipeline with single-question selection, explicit unknown support, recap-edit reopen logic, and history tracking.
- Extended schema/API contracts and tests so weather metadata and clarification state remain stable across iterative turns.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add confidence-aware extraction for timeline, weather, and budget normalization** - `aee1fd5` (feat)
2. **Task 2: Implement iterative clarification orchestration in SearchService** - `5c7e24c` (feat)

## Files Created/Modified
- `src/app/nlp/intent.py` - Adds slot metadata contract and normalized timeline/budget/weather extraction.
- `src/tests/nlp/test_intent_confidence.py` - Regression coverage for ambiguity thresholds and weather follow-up eligibility.
- `src/app/services/search.py` - Implements clarification turn orchestration, merge guards, history, and provider short-circuiting.
- `src/app/services/clarification.py` - Adds metadata-to-slot-state conversion, history helpers, and related-slot reopen behavior.
- `src/app/schemas/search.py` - Extends request/response and clarification models with weather and history fields.
- `src/app/api/v1/search.py` - Documents clarification/weather response behavior on search route.
- `src/tests/services/test_clarification_loop.py` - Verifies ordered single-question flow, explicit unknown progression, recap slot reopening, and weather carriage.
- `src/tests/api/test_search.py` - Verifies API result paths and clarification weather payload availability.

## Decisions Made
- Kept one global confidence threshold (`GLOBAL_CONFIDENCE_THRESHOLD`) across slots, including weather, to match D-10 and reduce threshold drift risk.
- Treated unresolved critical slots as a hard gate that skips provider execution, satisfying D-14 and threat mitigation T-01-05.
- Enforced slot-allowlist checks for answer/edit/update merge paths before `model_copy(update=...)` to mitigate slot tampering (T-01-04).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Capitalized sentence starter parsed as destination**
- **Found during:** Task 2
- **Issue:** Query `"Need a trip"` was incorrectly extracting `"Need"` as destination, breaking D-04 ordering tests.
- **Fix:** Expanded fallback stop-word filtering in `extract_intent` for capitalized non-location tokens.
- **Files modified:** `src/app/nlp/intent.py`
- **Verification:** `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py -x`
- **Committed in:** `5c7e24c`

**2. [Rule 1 - Bug] Dict-based clarification payloads crashed service path**
- **Found during:** Task 2
- **Issue:** Tests using `model_copy(update=...)` passed dict payloads for `clarification_answer`/`recap_edit`, causing attribute access errors.
- **Fix:** Added defensive validation/coercion in `_apply_clarification_turn` using `ClarificationAnswer.model_validate` and `ClarificationRecapEdit.model_validate`.
- **Files modified:** `src/app/services/search.py`
- **Verification:** `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -x`
- **Committed in:** `5c7e24c`

**3. [Rule 1 - Bug] Existing resolved request slots were overwritten by low-confidence extracted metadata**
- **Found during:** Task 2
- **Issue:** Provided destination/timeline/budget values were still treated unresolved because extractor metadata took precedence.
- **Fix:** Changed slot-state construction to prioritize explicit request values over extraction metadata when present.
- **Files modified:** `src/app/services/search.py`
- **Verification:** `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -x`
- **Committed in:** `5c7e24c`

---

**Total deviations:** 3 auto-fixed (3 bug fixes)
**Impact on plan:** No scope expansion; fixes were necessary to satisfy ordered clarification flow correctness.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Clarification control flow and extraction confidence metadata are now backend-complete and regression-tested.
- Ready for frontend interaction and end-to-end UX polish plans using stable clarification/weather payloads.

## Self-Check: PASSED
