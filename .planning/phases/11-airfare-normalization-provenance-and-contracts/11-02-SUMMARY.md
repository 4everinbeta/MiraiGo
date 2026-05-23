---
phase: 11-airfare-normalization-provenance-and-contracts
plan: 02
subsystem: api
tags: [fastapi, airfare, normalization, providers, pytest]
requires:
  - phase: 11-airfare-normalization-provenance-and-contracts
    provides: deterministic normalized airfare schema and helper utilities from 11-01
provides:
  - provider-native offer identifiers and stop/duration mapping inputs for normalization
  - SearchService normalization/provenance wiring on all flight results
  - API/service regression coverage for deterministic normalized airfare payloads
affects: [airfare-comparison, frontend-contract-consumers, phase-11-plan-03]
tech-stack:
  added: []
  patterns:
    - backend normalization applied during response assembly after deterministic interleave
    - null-present normalized contract with missing_fields enforcement
key-files:
  created: []
  modified:
    - src/app/providers/amadeus.py
    - src/app/providers/duffel.py
    - src/app/services/search.py
    - src/tests/providers/test_amadeus.py
    - src/tests/scrapers/test_duffel.py
    - src/tests/services/test_search_dual_provider.py
    - src/tests/api/test_search.py
key-decisions:
  - "Keep legacy airfare fields populated while layering canonical normalized/provenance fields at SearchService assembly."
  - "Normalize via helper then re-validate through FlightSearchResult to keep enum-typed schema authority."
patterns-established:
  - "Provider adapters pass provider_offer_id and raw summary values for downstream canonical normalization."
  - "Service/API tests assert deterministic normalized_offer_id and null-present missing_fields behavior."
requirements-completed: [AIR-03, AIR-04, AIR-08]
duration: 3 min
completed: 2026-05-23
---

# Phase 11 Plan 02: Canonical Provider-to-API Normalization Wiring Summary

**Search responses now emit deterministic normalized airfare IDs and provenance/freshness metadata across Amadeus and Duffel while preserving legacy fare fields for compatibility.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-05-23T00:22:43Z
- **Completed:** 2026-05-23T00:25:37Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- Added provider mapping passthrough for provider_offer_id and raw stop/duration summaries in both adapters.
- Wired canonical normalization into SearchService response assembly for every flight offer.
- Extended service/API regressions to enforce normalized/provenance contract determinism and null-present behavior.

## Task Commits

1. **Task 1: Add provider mapping inputs required for canonical normalization** - `838d2ca` (test), `9b2bbaf` (feat)
2. **Task 2: Wire normalization/provenance into SearchService response assembly** - `d254d33` (test), `5b587e3` (feat)
3. **Task 3: Add API and service regressions for deterministic normalized payload behavior** - `3258a53` (test)

## Files Created/Modified
- `src/app/providers/amadeus.py` - maps provider_offer_id and provider stop summary into FlightSearchResult.
- `src/app/providers/duffel.py` - maps provider_offer_id and slice stop summary into FlightSearchResult.
- `src/app/services/search.py` - applies `normalize_airfare_offer` and schema-validates normalized payloads.
- `src/tests/providers/test_amadeus.py` - verifies Amadeus normalization inputs are preserved.
- `src/tests/scrapers/test_duffel.py` - verifies Duffel normalization inputs are preserved.
- `src/tests/services/test_search_dual_provider.py` - asserts deterministic IDs, null contract behavior, and legacy compatibility.
- `src/tests/api/test_search.py` - asserts normalized/provenance response keys, null-present sparse contracts, and stable IDs across repeated calls.

## Decisions Made
- Kept normalization at SearchService assembly boundary to preserve existing provider retrieval/order semantics.
- Enforced normalized payload typing by validating merged normalized values through `FlightSearchResult`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Isolated service regression tests from Redis cache bleed**
- **Found during:** Task 2 (RED)
- **Issue:** repeated-call assertions caused cached cross-test result contamination.
- **Fix:** added an autouse fixture in service tests to stub redis `get/setex`.
- **Files modified:** `src/tests/services/test_search_dual_provider.py`
- **Verification:** `./venv/bin/pytest src/tests/services/test_search_dual_provider.py -q`
- **Committed in:** `d254d33`

**2. [Rule 1 - Bug] Removed enum serialization warnings after normalization updates**
- **Found during:** Task 2 (GREEN verification)
- **Issue:** `model_copy(update=...)` stored string enum values and emitted serialization warnings.
- **Fix:** re-validated normalized payloads via `FlightSearchResult.model_validate`.
- **Files modified:** `src/app/services/search.py`
- **Verification:** `./venv/bin/pytest src/tests/services/test_search_dual_provider.py -q`
- **Committed in:** `5b587e3`

---

**Total deviations:** 2 auto-fixed (2 Rule 1 bugs)  
**Impact on plan:** fixes were required for deterministic and warning-free contract behavior; no scope creep.

## Authentication Gates
None.

## Issues Encountered
- Task 3 regression assertions passed immediately because Task 2 implementation already satisfied the contract; retained test-only commit to lock behavior.

## Known Stubs
None.

## Next Phase Readiness
- Ready for 11-03 with normalized/provenance contracts enforced at provider, service, and API regression layers.
- No blockers.

## Self-Check: PASSED
- Found summary file: `.planning/phases/11-airfare-normalization-provenance-and-contracts/11-02-SUMMARY.md`
- Verified commits: `838d2ca`, `9b2bbaf`, `d254d33`, `5b587e3`, `3258a53`
