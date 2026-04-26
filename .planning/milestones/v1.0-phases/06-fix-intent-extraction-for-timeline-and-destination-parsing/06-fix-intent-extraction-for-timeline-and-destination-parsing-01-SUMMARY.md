# Phase 06 Plan 01 Summary

## Outcome

Destination and timeline extraction were hardened in `src/app/nlp/intent.py` so route/date phrasing is parsed more reliably while keeping existing contract fields stable.

## Implemented

- Added destination parsing helpers:
  - `_extract_destination`
  - `_is_destination_candidate`
  - `_normalize_location_candidate`
- Added `TIMELINE_TERMS` to block timeline-like values from being treated as destinations.
- Improved regex boundaries and precedence:
  - route parsing now uses explicit word boundaries for `from ... to ...`.
  - preposition parsing now differentiates `to|near|at` from `in` to avoid swallowing timeline phrases.
- Preserved existing output keys and behavior shape:
  - `location`
  - `date_range`
  - `normalized_timeline`
  - `slot_metadata`

## Test Coverage Added

- `src/tests/nlp/test_intent.py`
  - ignores timeline token as destination (`in June`)
  - accepts lowercase destination after preposition (`to lisbon`)
- `src/tests/nlp/test_intent_date_range.py`
  - route parsing with lowercase terms keeps destination and avoids false date range

## Files Changed

- `src/app/nlp/intent.py`
- `src/tests/nlp/test_intent.py`
- `src/tests/nlp/test_intent_date_range.py`
