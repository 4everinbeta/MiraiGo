---
phase: 09
slug: milestone-integration-validation-backfill
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-26
---

# Phase 09 — Validation Strategy

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

- **After every task commit:** Run quick command for touched layer.
- **After every plan wave:** Run full suite command.
- **Before `/gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | INTENT-02 | T-09-01 / — | Frontend/backend slot parity includes weather | api+ui | `PYTHONPATH=. ./venv/bin/pytest src/tests/api/test_search.py -q && cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false` | ✅ | ✅ green |
| 09-02-01 | 02 | 2 | INTENT-01..04 | T-09-02 / — | Phase 06 validation artifact and gate map are present and consistent | docs+tests | `grep -Eq "phase:\\s*06|nyquist_compliant" .planning/phases/06-fix-intent-extraction-for-timeline-and-destination-parsing/06-VALIDATION.md` | ✅ | ✅ green |
| 09-03-01 | 03 | 3 | INTENT-01..04 | T-09-03 / — | Verification metadata and milestone attestation remain deterministic | docs+full suite | `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q && cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `.planning/phases/06-fix-intent-extraction-for-timeline-and-destination-parsing/06-VALIDATION.md` — created in 09-02
- [x] normalize `status:` frontmatter in `06-VERIFICATION.md` and `07-VERIFICATION.md` — completed in 09-02

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Milestone-level cross-phase E2E attestation | INTENT-01..04 | Requires integrated artifact-level closure sign-off | Completed: `.planning/phases/09-milestone-integration-validation-backfill/09-MILESTONE-E2E-ATTESTATION.md` with canonical commands and outputs |

## Final Evidence Snapshot (2026-04-26)

- `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q` → `21 passed in 2.76s`
- `cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx --watch=false` → `Test Suites: 1 passed` / `Tests: 9 passed`
- `grep -n "^status:" .planning/phases/06-fix-intent-extraction-for-timeline-and-destination-parsing/06-VERIFICATION.md` → `4:status: complete`
- `grep -n "^status:" .planning/phases/07-enhanced-nlp/07-VERIFICATION.md` → `4:status: complete`

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
