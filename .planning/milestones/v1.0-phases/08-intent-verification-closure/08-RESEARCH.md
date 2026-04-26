# Phase 8: Intent Verification Closure - Research

**Researched:** 2026-04-25  
**Focus:** Close INTENT-01..04 verification debt with auditable automated + human evidence

## Key Findings

1. The blocking gap is verification state, not missing implementation: milestone audit shows INTENT-01..04 unsatisfied because Phase 1 verification is still `human_needed`.
2. Existing automated coverage is already strong in backend/service/UI tests and can be reused as canonical proof for INTENT requirements.
3. Phase 8 should be executed as a strict closure pipeline: evidence refresh, fresh human UAT, fix-any-critical-gap loop, then artifact/traceability updates.

## Requirement-to-Evidence Mapping

| Requirement | Automated evidence anchors | Human UAT evidence needed |
|---|---|---|
| INTENT-01 | `web/src/__tests__/Home.test.tsx`, API search route contract | Submit vague NL prompt in browser and confirm search/clarification starts correctly |
| INTENT-02 | `src/app/nlp/intent.py`, `src/tests/api/test_search.py` | Run multilingual/ambiguous prompts and confirm recap-extracted constraints are coherent |
| INTENT-03 | `src/app/services/clarification.py`, `src/tests/services/test_clarification_loop.py` | Confirm one-question-at-a-time focused follow-up behavior in real browser flow |
| INTENT-04 | `web/src/app/page.tsx`, `Home.test.tsx`, `test_clarification_loop.py` | Confirm continue flow does not restart or re-open resolved critical slots |

## Reusable Assets

- `src/tests/services/test_clarification_loop.py` (clarification order, slot reopen behavior, sequential continuity)
- `src/tests/api/test_search.py` (API-level clarification and extraction stability)
- `web/src/__tests__/Home.test.tsx` (turn continuity and payload/session preservation)
- `.planning/phases/01-intent-capture-clarification/01-VERIFICATION.md` (artifact format to reuse)

## Recommended Plan Slices

1. Evidence baseline refresh (rerun canonical automated suites and capture outputs)
2. Fresh human UAT closure pack (step-by-step reproducible checks for INTENT-01..04)
3. Conditional fix loop for any newly found INTENT-critical failures
4. Verification + traceability closure updates only after strict pass gates

## Risks / Watchouts

- Tests can pass while requirement remains unsatisfied if human evidence is missing.
- Any skipped INTENT-critical check violates Phase 8 closure bar.
- Frontend/backend clarification slot drift remains a watch area (`weather` enum mismatch risk).

## Validation Architecture

### Test Framework
- Backend: `pytest` suites under `src/tests/`
- Frontend: Jest/Testing Library suite under `web/src/__tests__/`

### Canonical Commands
- `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py -q`
- `PYTHONPATH=. ./venv/bin/pytest src/tests/api/test_search.py -q`
- `cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false`

### Phase Gate
Phase 8 passes only when:
1. INTENT-01..04 each have fresh automated evidence
2. INTENT-01..04 each have fresh human UAT pass evidence
3. Zero open blockers and zero skipped INTENT-critical checks
