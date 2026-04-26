---
phase: 06
slug: fix-intent-extraction-for-timeline-and-destination-parsing
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-26
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `src/tests/conftest.py` |
| **Quick run command** | `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp/test_intent.py -q` |
| **Full suite command** | `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp/test_intent.py src/tests/nlp/test_intent_confidence.py src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q` |
| **Estimated runtime** | ~180 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp/test_intent.py -q`
- **After every plan wave:** Run `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp/test_intent.py src/tests/nlp/test_intent_confidence.py src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -q`
- **Before `/gsd-verify-work`:** Full extraction + clarification + API chain must be green
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | INTENT-02 | — | Route phrasings do not overwrite canonical destination extraction. | unit | `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp/test_intent.py -q` | ✅ | ✅ green |
| 06-01-02 | 01 | 1 | INTENT-03 | — | Timeline parsing confidence gates clarification prompts safely. | unit | `PYTHONPATH=. ./venv/bin/pytest src/tests/nlp/test_intent_confidence.py -q` | ✅ | ✅ green |
| 06-01-03 | 01 | 1 | INTENT-04 | — | Clarification loop remains stable after extraction updates. | service | `PYTHONPATH=. ./venv/bin/pytest src/tests/services/test_clarification_loop.py -q` | ✅ | ✅ green |
| 06-01-04 | 01 | 1 | INTENT-02, INTENT-04 | — | API search request behavior remains deterministic with updated extraction outputs. | api | `PYTHONPATH=. ./venv/bin/pytest src/tests/api/test_search.py -q` | ✅ | ✅ green |

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Destination and timeline interpretation for natural phrasing | INTENT-02, INTENT-03 | Requires human semantic judgement | Submit “Plan flights from Denver to Miami for 7 days”; confirm destination=Miami with no incorrect absolute date range. |
| Date range extraction confidence and recap coherence | INTENT-03, INTENT-04 | Recap/follow-up readability is qualitative | Submit “Trip to Paris from December 1st to December 15th”; confirm parsed date_range and no redundant timeline re-ask. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 180s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved
