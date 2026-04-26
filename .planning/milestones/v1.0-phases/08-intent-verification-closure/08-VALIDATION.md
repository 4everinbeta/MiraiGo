---
phase: 08
slug: intent-verification-closure
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-25
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + jest |
| **Config file** | `src/tests/conftest.py`, `web/jest.config.ts` |
| **Quick run command** | `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py -q` |
| **Full suite command** | `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q && cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick command for the touched layer.
- **After every plan wave:** Run full suite command.
- **Before `/gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | INTENT-01 | T-08-01 / — | Prompt submit path remains valid and typed | ui integration | `cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false` | ✅ | ✅ green |
| 08-01-02 | 01 | 1 | INTENT-02 | T-08-02 / — | Structured slot extraction remains stable | api/service | `PYTHONPATH=. ./venv/bin/pytest src/tests/api/test_search.py -q` | ✅ | ✅ green |
| 08-01-03 | 01 | 1 | INTENT-03 | T-08-03 / — | Follow-ups remain focused and ordered | service | `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py -q` | ✅ | ✅ green |
| 08-02-01 | 02 | 2 | INTENT-04 | T-08-04 / — | Continue flow keeps session continuity | ui+service | `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py -q && cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false` | ✅ | ✅ green |
| 08-02-02 | 02 | 2 | INTENT-01..04 | T-08-05 / T-08-06 | Human UAT closure + strict blocked/skipped gate evidence stays zero after rerun | docs+full suite | `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q && cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false && cd .. && grep -Eq "blocked:\\s*0" .planning/phases/01-intent-capture-clarification/01-HUMAN-UAT.md && grep -Eq "skipped:\\s*0" .planning/phases/01-intent-capture-clarification/01-HUMAN-UAT.md && grep -Eq "blocked:\\s*0" .planning/phases/01-intent-capture-clarification/01-VERIFICATION.md && grep -Eq "skipped:\\s*0" .planning/phases/01-intent-capture-clarification/01-VERIFICATION.md && grep -Eq "blocked:\\s*0" .planning/phases/08-intent-verification-closure/08-VALIDATION.md && grep -Eq "skipped:\\s*0" .planning/phases/08-intent-verification-closure/08-VALIDATION.md` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Strict INTENT Gate Snapshot (D8-02)

**Captured:** 2026-04-26  
**Policy:** Hard-fail closure unless both totals below remain zero.

- blocked: 0
- skipped: 0

### Requirement Gate Matrix

| Requirement | Automated Evidence | Latest Result | blocked | skipped |
|---|---|---|---:|---:|
| INTENT-01 | `web/src/__tests__/Home.test.tsx` (`renders initial state...`, free-form prompt submit flows) | PASS | 0 | 0 |
| INTENT-02 | `src/tests/api/test_search.py` (`test_post_search_multilingual_destination_and_synonym_keep_clarification_flow`) | PASS | 0 | 0 |
| INTENT-03 | `src/tests/services/test_clarification_loop.py` (`test_missing_slots_are_asked_in_priority_order_one_by_one`) | PASS | 0 | 0 |
| INTENT-04 | `src/tests/api/test_search.py` + `src/tests/services/test_clarification_loop.py` + `web/src/__tests__/Home.test.tsx` (`test_search_handles_follow_up_clarification_turn`, `test_continue_turn_with_preserved_resolved_fields...`, `preserves resolved clarification fields on Continue`) | PASS | 0 | 0 |

### Final INTENT Dual-Evidence Closure Sync (Phase 08 Plan 03)

| Requirement | Automated Evidence | Human Evidence | Final |
|---|---|---|---|
| INTENT-01 | `web/src/__tests__/Home.test.tsx` prompt submit assertions | `01-HUMAN-UAT.md` test 1 (pass) | ✓ VERIFIED |
| INTENT-02 | `src/tests/api/test_search.py` extraction stability test | `01-HUMAN-UAT.md` test 2 (pass) | ✓ VERIFIED |
| INTENT-03 | `src/tests/services/test_clarification_loop.py` slot-priority follow-up test | `01-HUMAN-UAT.md` test 3 (pass) | ✓ VERIFIED |
| INTENT-04 | API + service + UI continue-turn continuity tests | `01-HUMAN-UAT.md` test 4 (pass) | ✓ VERIFIED |

### Machine-Check Enforcement

```bash
PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q \
  && cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false \
  && cd .. \
  && grep -Eq "blocked:\\s*0" .planning/phases/08-intent-verification-closure/08-VALIDATION.md \
  && grep -Eq "skipped:\\s*0" .planning/phases/08-intent-verification-closure/08-VALIDATION.md
```

Any non-zero `blocked` or `skipped` value fails this gate.

### 08-02 Remediation Loop Outcome (D8-03)

- result: no-fix-needed
- basis: checkpoint approved for fresh browser UAT (INTENT-01..04 all pass)
- blocked: 0
- skipped: 0

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real browser continuity after clarification | INTENT-04 | UX continuity cannot be fully asserted via mocks | Run vague prompt -> answer trip length + budget -> continue; verify no critical-slot reopen/restart |
| Follow-up clarity/readability in recap and prompts | INTENT-03 | Human clarity and affordance quality | Run a missing-slot flow and confirm one focused prompt at a time with understandable recap text |

---

## Validation Audit 2026-04-26

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 180s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved
