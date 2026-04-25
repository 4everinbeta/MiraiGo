---
phase: 01-intent-capture-clarification
plan: 01
subsystem: api
tags: [fastapi, pydantic, clarification, react, typescript, testing]
requires:
  - phase: 01-intent-capture-clarification
    provides: UI contract and intent clarification decisions (D-01..D-16)
provides:
  - Canonical backend clarification request/response schema contract
  - Clarification helper module with slot ordering, thresholding, and dependency graph
  - Frontend API contract parity for clarification turns and recap edits
  - Wave 0 backend/frontend clarification contract tests
affects: [search-service, search-ui, follow-up-loop, recap-edit-flow]
tech-stack:
  added: []
  patterns: [one-question clarification selection, explicit unknown-slot representation, frontend-backend contract parity]
key-files:
  created:
    - src/app/services/clarification.py
    - src/tests/services/test_clarification_loop.py
    - web/src/components/search/__tests__/ClarificationFlow.test.tsx
  modified:
    - src/app/schemas/search.py
    - src/app/api/v1/search.py
    - src/tests/schemas/test_search_schemas.py
    - web/src/lib/api.ts
key-decisions:
  - "Use ClarificationSlot enum-backed schema fields to constrain allowed slot keys at the validation boundary."
  - "Allow clarification-only SearchRequest updates without requiring query/destination to preserve iterative turns."
patterns-established:
  - "Clarification state always returns slot-level confidence, ambiguity, and explicit unknown metadata."
  - "Follow-up selection is deterministic via CRITICAL_SLOT_ORDER and a single GLOBAL_CONFIDENCE_THRESHOLD."
requirements-completed: [INTENT-02, INTENT-03, INTENT-04]
duration: 1min
completed: 2026-04-25
---

# Phase 01 Plan 01: Intent Capture Clarification Contracts Summary

**Typed clarification contracts now drive backend and frontend turn payloads with deterministic one-question selection and explicit unknown-state handling.**

## Performance

- **Duration:** 1 min
- **Started:** 2026-04-25T00:25:18Z
- **Completed:** 2026-04-25T00:25:58Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- Added backend clarification models (state, question, recap, answer/edit/update payloads) and wired `SearchRequest` / `SearchResponse` contract fields.
- Implemented pure clarification helpers with critical slot order, global confidence threshold, one-question selection, stop conditions, and related-slot graph constants.
- Added frontend clarification API types plus Wave 0 backend/frontend test scaffolds with concrete assertions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create canonical clarification contracts and dependency graph constants** - `bc57eb9` (feat)
2. **Task 2: Mirror clarification contracts in frontend API client types** - `d12cc29` (feat)
3. **Task 3: Add Wave 0 clarification test scaffolds that enforce the new contracts** - `25302ac` (test)

## Files Created/Modified
- `src/app/schemas/search.py` - Clarification schema models and request/response contract extensions.
- `src/app/services/clarification.py` - Slot ordering, confidence threshold, next-question logic, recap generation, and dependency graph.
- `src/app/api/v1/search.py` - Route-level clarification contract annotation context.
- `src/tests/schemas/test_search_schemas.py` - Clarification-aware request validation test coverage.
- `web/src/lib/api.ts` - Frontend clarification contract interfaces and request fields.
- `src/tests/services/test_clarification_loop.py` - Backend contract behavior tests for ordering and next-question logic.
- `web/src/components/search/__tests__/ClarificationFlow.test.tsx` - Frontend typed clarification rendering scaffold test.

## Decisions Made
- Used enum-constrained slot identifiers (`ClarificationSlot`) for all clarification payloads to satisfy threat mitigation T-01-01.
- Kept clarification iterative by allowing query-less/destination-less requests when clarification update fields are supplied.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Pytest binary missing in shell PATH**
- **Found during:** Task 1 verification
- **Issue:** `pytest` command was unavailable (`command not found`) in current shell environment.
- **Fix:** Switched verification commands to `./venv/bin/pytest` to run within the project virtual environment.
- **Files modified:** None (execution environment only)
- **Verification:** All required backend tests passed using venv-scoped pytest.
- **Committed in:** `bc57eb9` (task verification path; no code delta for this fix)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change; fix only affected command execution context.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Backend and frontend now share a concrete clarification contract baseline.
- Wave 0 tests are in place to support RED/GREEN work in downstream clarification behavior and UI plans.

## Self-Check: PASSED
