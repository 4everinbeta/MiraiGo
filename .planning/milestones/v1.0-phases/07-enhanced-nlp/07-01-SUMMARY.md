# Phase 07 Plan 01 Summary

## Outcome

Intent extraction accuracy and ambiguity handling were hardened so destination/timeline parsing is more deterministic and uncertain phrasing is scored conservatively.

## Implemented

- Added deterministic helper extraction flow in `src/app/nlp/intent.py`:
  - `_normalize_query`
  - `_contains_phrase`
  - `_extract_qualities`
  - `_extract_modes`
  - `_extract_budget`
  - `_extract_duration_days`
  - `_contains_uncertainty`
- Improved destination parsing safety:
  - guarded multilingual route/preposition patterns to reduce false location captures
  - added stop-token handling for connectors that previously leaked into destination values
- Tightened timeline extraction:
  - `between ... and ...` now validates timeline fragments before assigning `date_range`
- Kept clarification compatibility by preserving `slot_metadata` semantics and uncertainty lowering behavior.

## Test Coverage Added

- `src/tests/nlp/test_intent.py`
  - multilingual destination/budget/date token coverage
- `src/tests/nlp/test_intent_confidence.py`
  - unsupported-language ambiguity/low-confidence behavior
- `src/tests/services/test_clarification_loop.py`
  - uncertain prompt still asks destination first

## Files Changed

- `src/app/nlp/intent.py`
- `src/tests/nlp/test_intent.py`
- `src/tests/nlp/test_intent_confidence.py`
- `src/tests/services/test_clarification_loop.py`
