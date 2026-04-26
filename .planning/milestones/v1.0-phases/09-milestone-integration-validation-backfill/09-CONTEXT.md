# Phase 9: Milestone Integration & Validation Backfill - Context

**Gathered:** 2026-04-26  
**Status:** Ready for planning

## Phase Boundary

Close remaining milestone blockers after Phase 8 by:
1. Resolving cross-phase integration parity gaps.
2. Backfilling missing validation/verification metadata artifacts.
3. Capturing one explicit milestone-level E2E attestation before re-audit.

In scope:
- Clarification slot parity (`weather`) between backend and frontend contracts.
- Creation of Phase 06 validation artifact and deterministic verification metadata normalization for 06/07.
- One fresh cross-phase E2E attestation artifact for milestone closure evidence.

Out of scope:
- New recommendation/pricing/discovery feature delivery (Phases 2-5 scope).
- Re-opening Phase 8 INTENT closure decisions unless regressions are found.

## Locked Decisions

- **D9-01:** Backend `ClarificationSlot` enum is canonical; frontend types/tests must align to it.
- **D9-02:** Closure bar requires `06-VALIDATION.md`, explicit frontmatter `status` in `06-VERIFICATION.md` and `07-VERIFICATION.md`, and rerun evidence tied to those artifact updates.
- **D9-03:** Phase 9 must include one explicit milestone-level cross-phase E2E attestation captured in artifacts before re-running milestone audit.

## Prior Context Applied (Do Not Re-decide)

- Phase 8 already closed INTENT-01..04 requirement debt with strict `blocked: 0` and `skipped: 0` gates.
- Latest milestone audit is now requirement-satisfied but still `gaps_found` due integration/validation/metadata determinism gaps.
- Phase 9 is the designated gap-closure phase in ROADMAP.

## Canonical References

- `.planning/ROADMAP.md` (Phase 9 goals/plans)
- `.planning/REQUIREMENTS.md` (INTENT traceability state)
- `.planning/v1.0-v1.0-MILESTONE-AUDIT.md` (current open blockers)
- `.planning/phases/06-fix-intent-extraction-for-timeline-and-destination-parsing/06-VERIFICATION.md`
- `.planning/phases/07-enhanced-nlp/07-VERIFICATION.md`
- `.planning/phases/08-intent-verification-closure/08-VERIFICATION.md`
- `.planning/phases/08-intent-verification-closure/08-VALIDATION.md`
- `src/app/schemas/search.py`
- `web/src/lib/api.ts`
- `src/tests/api/test_search.py`
- `src/tests/services/test_clarification_loop.py`
- `web/src/__tests__/Home.test.tsx`
- `web/src/app/page.tsx`
- `web/src/components/search/SearchForm.tsx`

## Reusable Assets & Patterns

- Existing strict-gate evidence style from Phase 8 validation/verification artifacts.
- Existing clarification continuity and API integration regression suites (`test_search.py`, `test_clarification_loop.py`, `Home.test.tsx`).
- Existing milestone audit format (`v1.0-v1.0-MILESTONE-AUDIT.md`) for deterministic blocker reporting.

## Risks / Watchouts

- Contract alignment changes can silently desync frontend mocks/types if tests are not updated in lockstep.
- Metadata-only updates without rerun proof will fail milestone closure determinism.
- E2E attestation must be explicit and reproducible, not implied by scattered test outputs.

## Open Questions Resolved in Discuss

All identified gray areas for Phase 9 are resolved by D9-01 through D9-03. No unresolved scope decisions remain for planning.

## Next Step for Planner

Create Phase 9 plans that explicitly deliver:
1. Frontend/backend clarification slot parity with regression coverage.
2. Phase 06 validation backfill + 06/07 verification status normalization with rerun evidence.
3. A concrete milestone-level E2E attestation artifact and re-audit-ready closure packaging.
