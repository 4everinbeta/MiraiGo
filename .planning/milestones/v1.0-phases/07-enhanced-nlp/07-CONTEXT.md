# Phase 7: Enhanced NLP - Context

**Gathered:** 2026-04-25  
**Status:** Ready for planning

## Phase Boundary

Improve natural-language search intent handling across three areas in one phase:
1. Intent extraction accuracy and ambiguity handling.
2. Multilingual query support.
3. Entity synonym expansion for destinations, activities, and weather.

## Locked Decisions

- **D7-01:** Phase 7 includes all three NLP tracks in a single phase.
- **D7-02:** Existing API request/response contracts remain backward compatible.
- **D7-03:** Clarification loop behavior must stay deterministic and continue to use slot metadata confidence/ambiguity.
- **D7-04:** Improvements are additive; no removal of current English-first behavior during rollout.

## Canonical References

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md` (INTENT-02, INTENT-03, INTENT-04)
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `src/app/nlp/intent.py`
- `src/app/services/search.py`
- `src/app/services/clarification.py`
- `src/tests/nlp/*`
- `src/tests/services/test_clarification_loop.py`

## Risks / Concerns

- Broad NLP changes can regress existing extraction.
- Multilingual normalization may reduce confidence quality if language detection is weak.
- Synonym expansion can introduce false positives in destination and quality extraction.
