---
phase: 07
slug: enhanced-nlp
status: verified
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-25
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + jest |
| **Config file** | `web/jest.config.ts` |
| **Quick run command** | `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py -q` |
| **Full suite command** | `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q && cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx` |
| **Estimated runtime** | ~240 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py -q`
- **After every plan wave:** Run `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q`
- **Before `/gsd-verify-work`:** Full backend + Home integration suite must be green
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | INTENT-02, INTENT-03, INTENT-04 | — | Parser avoids false-positive destination/timeline extraction under ambiguity. | unit | `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp/test_intent.py src/tests/nlp/test_intent_confidence.py -q` | ✅ | ✅ green |
| 07-02-01 | 02 | 2 | INTENT-02, INTENT-03 | — | Multilingual normalization maps to canonical slots without unsafe fallback behavior. | unit | `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp/test_intent_multimodal.py -q` | ✅ | ✅ green |
| 07-03-01 | 03 | 3 | INTENT-02, INTENT-03, INTENT-04 | — | Synonym expansion preserves deterministic clarification/API behavior. | unit+api | `PYTHONPATH=. ./venv/bin/pytest src/tests/api/test_search.py -q` | ✅ | ✅ green |
| 07-04-01 | 04 | 4 | INTENT-02, INTENT-03 | — | Guarded `a <destination>` pattern supports romance-language travel prompts without article false positives. | unit | `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp/test_intent_multimodal.py -q` | ✅ | ✅ green |
| 07-05-01 | 05 | 4 | INTENT-04 | — | Clarification session preserves resolved slots across recap edits and follow-up turns. | integration | `cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx` | ✅ | ✅ green |
| 07-06-01 | 06 | 5 | INTENT-03, INTENT-04 | — | Timeline follow-up policy avoids redundant re-asks when timeline is concretely present. | unit | `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py -q` | ✅ | ✅ green |

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| End-user conversational UX perception (copy clarity and subjective trust) | INTENT-04 | Subjective usability judgment | Run `/gsd-verify-work 7` and capture user wording feedback in `07-UAT.md`. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 240s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-25
