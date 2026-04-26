# Phase 6: Fix intent extraction for timeline and destination parsing - Context

**Gathered:** 2026-04-25  
**Status:** Ready for planning

## Phase Boundary

Stabilize NLP extraction behavior for destination and timeline parsing so travel queries with route phrases, date windows, and ambiguous natural language produce consistent slot metadata and clarification triggers.

## Decisions

- **D6-01:** Keep extraction implementation in `src/app/nlp/intent.py`; do not introduce new parsing services for this phase.
- **D6-02:** Timeline parsing must distinguish route phrases (`from X to Y`) from date-range phrases (`from DATE to DATE`).
- **D6-03:** Destination extraction should prefer geographic entities and avoid false positives from timeline/date fragments.
- **D6-04:** Any low-confidence/ambiguous destination or timeline parse must preserve clarification eligibility through slot metadata.
- **D6-05:** Backward compatibility fields (`location`, `date_range`, `normalized_timeline`, `slot_metadata`) remain stable for API consumers.

## Canonical References

- `.planning/ROADMAP.md` (Phase 6 section)
- `.planning/REQUIREMENTS.md` (INTENT-02, INTENT-03, INTENT-04)
- `src/app/nlp/intent.py`
- `src/app/services/search.py`
- `src/tests/nlp/test_intent*.py`
- `src/tests/services/test_clarification_loop.py`

## Known Risks

- Regex changes can regress existing extraction behavior.
- Route/date token overlap can silently degrade timeline parsing.
- Frontend clarification UX depends on confidence and ambiguity fields remaining coherent.
