# Phase 8: Intent Verification Closure - Context

**Gathered:** 2026-04-25  
**Status:** Ready for planning

## Phase Boundary

Close milestone-audit verification debt for INTENT-01 through INTENT-04 by converting Phase 1 from `human_needed` to fully verified with auditable automated and human evidence.

In scope:
1. Verification closure for INTENT-01..04 only.
2. Evidence refresh after Phase 07 NLP and clarification changes.
3. Requirement traceability status update once closure bar is met.

Out of scope:
1. Phase 9 integration/Nyquist backfill work.
2. New product features outside intent/clarification verification closure.

## Locked Decisions

- **D8-01:** Each INTENT requirement must include **both** automated test evidence and a fresh human UAT pass.
- **D8-02:** Closure bar is strict: all INTENT-01..04 must pass with zero open blockers and no skipped critical checks.
- **D8-03:** If new INTENT-critical UAT failures appear, they must be fixed in Phase 8 before closure (no deferral to Phase 9).

## Revision Directives (Checker Alignment)

- Automated verify commands must **hard-fail** unless `blocked: 0` and `skipped: 0` are present for INTENT-critical closure checks.
- Scope must stay layer-targeted during remediation (avoid broad cross-stack edits in a single task unless a cross-layer failing assertion proves necessity).
- Keep explicit requirement traceability for INTENT-01..04 in every closure artifact update.

## Prior Context Applied (Do Not Re-decide)

- Phase 1 established critical-slot clarification policy, one-question-at-a-time flow, and recap edit behavior.
- Phase 7 already improved multilingual NLP, synonym handling, and clarification continuity behavior.
- Milestone audit identified exact unresolved requirement debt source: Phase 1 verification status remains `human_needed`.

## Canonical References

- `.planning/ROADMAP.md` (Phase 8/9 definitions)
- `.planning/REQUIREMENTS.md` (INTENT-01..04)
- `.planning/v1.0-v1.0-MILESTONE-AUDIT.md` (current gaps and closure targets)
- `.planning/phases/01-intent-capture-clarification/01-VERIFICATION.md` (current `human_needed` evidence baseline)
- `.planning/phases/07-enhanced-nlp/07-UAT.md` (recent UAT outcomes and skipped-item history)
- `src/app/services/search.py`
- `src/app/services/clarification.py`
- `src/app/nlp/intent.py`
- `src/tests/services/test_clarification_loop.py`
- `src/tests/api/test_search.py`
- `web/src/__tests__/Home.test.tsx`

## Reusable Assets & Patterns

- Existing backend/ frontend regression coverage already targets clarification sequencing and turn continuity.
- Existing verification artifact format in `01-VERIFICATION.md` should be reused for consistency.
- Existing UAT workflow/docs in Phase 07 provide a template for writing reproducible human checks.

## Open Questions Resolved in Discuss

All identified Phase 8 gray areas are resolved by D8-01 through D8-03. No additional unresolved design questions remain for planning.

## Risks / Watchouts

- Human verification must be reproducible and concrete, not subjective-only UX notes.
- Automated tests can pass while browser-session continuity still regresses; Phase 8 requires both forms of evidence.
- Requirement closure must align with milestone audit expectations to avoid re-opening INTENT gaps later.

## Next Step for Planner

Create Phase 8 plan(s) that explicitly map each INTENT requirement to:
1. Automated test evidence (file + scenario coverage)
2. Human UAT steps and expected outcomes
3. Pass/fail gating rules that enforce D8-02 and D8-03
4. Verification artifact updates that flip requirement status from unsatisfied/pending to satisfied only when gates are met
