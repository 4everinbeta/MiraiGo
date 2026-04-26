# Phase 9: Milestone Integration & Validation Backfill - Research

**Researched:** 2026-04-26  
**Focus:** Integration parity + validation backfill + milestone closure determinism

## Key Findings

1. Integration gap is concrete: backend `ClarificationSlot` includes `weather`, frontend typed slot union does not (`src/app/schemas/search.py` vs `web/src/lib/api.ts`).
2. Milestone audit blockers are now artifact-level/determinism-level: missing `06-VALIDATION.md`, plus missing explicit `status` frontmatter in `06-VERIFICATION.md` and `07-VERIFICATION.md`.
3. Existing regression suites already provide strong coverage and should be reused as closure proof (`test_search.py`, `test_clarification_loop.py`, `Home.test.tsx`).

## Requirement-to-Evidence Strategy

| Requirement | Phase 9 evidence strategy |
|---|---|
| INTENT-01 | Preserve prompt-start integration checks in Home test reruns and attestation artifact |
| INTENT-02 | Align weather slot contract parity and keep API extraction/regression evidence green |
| INTENT-03 | Preserve one-question clarification order evidence via service tests |
| INTENT-04 | Preserve continue-flow continuity evidence via API + UI reruns and milestone E2E attestation |

## Recommended Plan Slices

1. **Contract parity slice:** make frontend clarification slot typing canonical with backend enum (`weather`) and update related tests.
2. **Validation/metadata slice:** create `06-VALIDATION.md` and normalize `status` in 06/07 verification frontmatter with rerun-linked evidence.
3. **Milestone closure slice:** add one explicit cross-phase E2E attestation artifact and refresh milestone audit from updated evidence.

## Reusable Assets

- `src/tests/api/test_search.py`
- `src/tests/services/test_clarification_loop.py`
- `web/src/__tests__/Home.test.tsx`
- Phase 8 strict gate pattern in `.planning/phases/08-intent-verification-closure/08-VALIDATION.md`

## Risks / Watchouts

- Fixing type parity without mock/test updates can leave hidden drift.
- Metadata-only edits without rerun evidence will not hold milestone audit closure.
- E2E attestation must be explicit and reproducible, not implied by scattered logs.

## Validation Architecture

### Canonical Commands

- `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q`
- `cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false`

### Wave 0 Gaps

- Missing `.planning/phases/06-fix-intent-extraction-for-timeline-and-destination-parsing/06-VALIDATION.md`
- Missing explicit `status:` frontmatter in:
  - `.planning/phases/06-fix-intent-extraction-for-timeline-and-destination-parsing/06-VERIFICATION.md`
  - `.planning/phases/07-enhanced-nlp/07-VERIFICATION.md`
