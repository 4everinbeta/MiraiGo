---
phase: 11-airfare-normalization-provenance-and-contracts
plan: 01
subsystem: api
tags: [airfare, pydantic, normalization, contracts]
requires:
  - phase: 10-dual-provider-realtime-airfare-retrieval
    provides: deterministic provider fan-out and flight result assembly
provides:
  - Canonical normalized airfare and provenance contract fields on FlightSearchResult
  - Deterministic pure normalization helpers for schema-aligned payload shaping
  - Regression tests for null-presence and stable normalized_offer_id behavior
affects: [phase-11-plan-02, web-contract-mirroring]
tech-stack:
  added: []
  patterns: [backend-schema-first contracts, pure deterministic normalization helpers]
key-files:
  created:
    - src/app/services/airfare_normalization.py
    - src/tests/services/test_airfare_normalization.py
  modified:
    - src/app/schemas/search.py
    - src/tests/schemas/test_search_schemas.py
key-decisions:
  - "Kept legacy flight fare fields on FlightSearchResult with explicit DEPRECATED descriptions for one-phase migration safety."
  - "Generated normalized_offer_id from canonical sorted JSON + SHA-256 hash over provider/route/time/price primitives."
patterns-established:
  - "Normalization helpers emit deterministic null-present keys with sorted missing_fields."
  - "Provenance/freshness containers are always present with nullable fields for stable contracts."
requirements-completed: [AIR-03, AIR-04, AIR-08]
duration: 3min
completed: 2026-05-23
---

# Phase 11 Plan 01: Airfare Normalization, Provenance, and Contracts Summary

**Backend flight contracts now expose deterministic normalized fare/provenance fields backed by pure normalization helpers with stable offer identity hashing.**

## Performance

- **Duration:** 3min
- **Started:** 2026-05-23T00:16:37Z
- **Completed:** 2026-05-23T00:19:16Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Extended `FlightSearchResult` with canonical normalized fare keys, conversion state, and provenance/freshness containers.
- Preserved legacy airfare fields with explicit deprecation metadata for migration continuity.
- Added a pure `airfare_normalization` helper module with deterministic hashing and sorted missing-field output.

## Task Commits

1. **Task 1: Extend Pydantic airfare contracts with normalized and provenance fields**
   - `cc2e692` (test) RED schema coverage
   - `e5b0a66` (feat) GREEN schema implementation
2. **Task 2: Create deterministic airfare normalization helper module**
   - `675e191` (test) RED normalization coverage
   - `0660698` (feat) GREEN helper implementation

## Files Created/Modified
- `src/app/schemas/search.py` - Added normalized airfare, conversion, provenance, freshness, and deprecation metadata fields.
- `src/app/services/airfare_normalization.py` - Implemented pure canonical normalization and deterministic `normalized_offer_id` generation.
- `src/tests/schemas/test_search_schemas.py` - Added schema contract tests for normalized/null-present/deprecation behavior.
- `src/tests/services/test_airfare_normalization.py` - Added deterministic normalization helper tests.

## Decisions Made
- Used `ConversionStatus` enum-backed values in normalization output for deterministic conversion-state semantics.
- Kept normalization helper as pure function module (no provider/network coupling) to match service helper pattern.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Backend normalization contracts are stable and test-covered for downstream wiring/mirroring.
- No blockers identified for Phase 11 follow-on plans.

## Self-Check: PASSED

- FOUND: `.planning/phases/11-airfare-normalization-provenance-and-contracts/11-01-SUMMARY.md`
- FOUND commits: `cc2e692`, `e5b0a66`, `675e191`, `0660698`
