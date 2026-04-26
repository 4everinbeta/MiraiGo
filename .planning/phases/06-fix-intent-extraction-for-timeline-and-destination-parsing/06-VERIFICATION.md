---
phase: 06-fix-intent-extraction-for-timeline-and-destination-parsing
verified: 2026-04-26T14:34:49Z
status: complete
---

# Phase 06 Verification Strategy

## Goal-Backward Checks

Phase 06 is complete only when these are true:

1. Timeline and destination extraction produce expected values for route/date edge phrasing.
2. Slot confidence + ambiguity values still drive clarification correctly.
3. No regressions in existing NLP and clarification tests.

## Required Evidence

- Passing NLP test suite sections for intent extraction.
- Passing clarification loop tests.
- Passing API search tests that rely on extraction outcomes.

## Human Spot Checks

1. Submit: "Plan flights from Denver to Miami for 7 days"  
   Expected: destination from route context; no false date range.
2. Submit: "Trip to Paris from December 1st to December 15th"  
   Expected: destination Paris; date_range start/end parsed; timeline slot high confidence.

## Fresh Rerun Evidence (2026-04-26)

- Command: `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q`
- Result: `21 passed in 2.75s`
