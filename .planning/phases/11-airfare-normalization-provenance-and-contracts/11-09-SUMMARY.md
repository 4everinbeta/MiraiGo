---
phase: 11-airfare-normalization-provenance-and-contracts
plan: 09
subsystem: api
tags: [nlp, airfare, clarification, react, contracts, testing]
requires:
  - phase: 11-08
    provides: deterministic no-flight guidance and blocked-continue contract fields
provides:
  - route/timeline airfare intent extraction that captures origin-destination hints for natural prompts
  - deterministic request-resolution merge of extracted signals before flight prerequisite gating
  - explicit requirement-keyed blocked-airfare remediation guidance in SearchForm
affects: [AIR-03, AIR-08, search-service, nlp, frontend-clarification]
tech-stack:
  added: []
  patterns:
    - extract route/date hints first, then gate flights using shared prerequisite helpers
    - keep backend schema as contract authority and frontend remediation typed via constraint_updates
key-files:
  created: []
  modified:
    - src/app/nlp/intent.py
    - src/app/services/search.py
    - src/tests/nlp/test_intent.py
    - src/tests/services/test_clarification_loop.py
    - src/tests/api/test_search.py
    - web/src/components/search/SearchForm.tsx
    - web/src/components/search/__tests__/ClarificationFlow.test.tsx
key-decisions:
  - "Prefer explicit route-hint extraction (from→to / to→from) over generic location heuristics for airfare prompts."
  - "Apply extracted destination, origin, and timeline windows during _resolve_request before flight gating."
  - "Render blocked-remediation guidance from pending requirement keys rather than warning-text parsing."
patterns-established:
  - "Airfare intent progression: query extraction -> typed request updates -> shared prerequisite gating."
  - "Blocked continue UX uses flight_requirements_pending contract keys to drive guidance and controls."
requirements-completed: [AIR-03, AIR-08]
duration: 15min
completed: 2026-05-24
---

# Phase 11 Plan 09: Airfare Intent Gap Closure Summary

**Airfare natural prompts now resolve route and timeline hints into flight-searchable constraints with deterministic blocked-remediation guidance end to end.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-05-24T15:29:05Z
- **Completed:** 2026-05-24T15:44:00Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- Added RED regressions for NLP, service, API, and UI contracts reproducing the UAT airfare intent failure.
- Implemented backend route/timeline/origin extraction merge before flight prerequisite gating.
- Added explicit requirement-keyed blocked-airfare guidance in SearchForm while preserving typed `constraint_updates` remediation flow.

## Task Commits

1. **Task 1: Add failing regressions for airfare-intent capture and progression** - `33fe7ec` (test)
2. **Task 2: Implement backend airfare intent-to-constraint capture and progression fixes** - `05b45d4` (feat)
3. **Task 3: Implement explicit airfare blocked-progression UX guidance in SearchForm** - `abd8f0c` (feat)

_Note: TDD cycle applied (RED then GREEN commits across task sequence)._

## Files Created/Modified
- `src/app/nlp/intent.py` - Added route hint extraction and origin hint output for airfare prompts.
- `src/app/services/search.py` - Added pre-gating intent signal merge for destination/origin/date_range and hardened origin parsing.
- `src/tests/nlp/test_intent.py` - Added regression for route destination + loose timeline extraction.
- `src/tests/services/test_clarification_loop.py` - Added regression for deterministic unblocked prerequisites after extraction.
- `src/tests/api/test_search.py` - Added API regression ensuring no silent empty airfare results for natural prompts.
- `web/src/components/search/SearchForm.tsx` - Added pending-requirement guidance bullets for blocked airfare progression.
- `web/src/components/search/__tests__/ClarificationFlow.test.tsx` - Added UI regression for requirement-keyed guidance copy.

## Decisions Made
- Route phrasing in airfare prompts now takes precedence via explicit route hint parsing to prevent origin/destination swaps.
- `_resolve_request` now applies extraction-derived date ranges from normalized timeline windows before prerequisite gating.
- UI blocked remediation messaging is generated from server-provided pending requirement keys to stay deterministic and contract-driven.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Airfare intent capture/regression gap is closed and contract-locked across NLP/service/API/UI tests.
- Ready for verifier/UAT rerun against the previously failing airfare natural-language scenario.

## Self-Check: PASSED
