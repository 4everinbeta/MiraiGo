---
phase: 01
slug: intent-capture-clarification
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-25
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (backend), Jest + Testing Library (frontend), Playwright (e2e) |
| **Config file** | `web/jest.config.ts`, `web/playwright.config.ts`, backend via pytest defaults + `src/tests/conftest.py` |
| **Quick run command** | `PYTHONPATH=. pytest src/tests/nlp/test_intent_confidence.py src/tests/services/test_clarification_loop.py -x && cd web && npm test -- --runInBand --testPathPatterns=ClarificationFlow.test.tsx` |
| **Full suite command** | `PYTHONPATH=. pytest -x && cd web && npm test -- --runInBand && cd web && npx playwright test tests/e2e/clarification.spec.ts --project=chromium` |
| **Estimated runtime** | ~180 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. pytest src/tests/nlp/test_intent_confidence.py src/tests/services/test_clarification_loop.py -x && cd web && npm test -- --runInBand --testPathPatterns=ClarificationFlow.test.tsx`
- **After every plan wave:** Run `PYTHONPATH=. pytest -x && cd web && npm test -- --runInBand`
- **Before `/gsd-verify-work`:** Full suite must be green, including Playwright clarification e2e
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | INTENT-02, INTENT-03 | T-01-01, T-01-02 | Clarification contract constrains slot keys and validates answer payload sizes | unit/schema | `PYTHONPATH=. pytest src/tests/schemas/test_search_schemas.py -k "clarification or search_request" -x` | ✅ | ⬜ pending |
| 01-01-02 | 01 | 1 | INTENT-04 | T-01-03 | Frontend API contract includes explicit unknown + typed clarification payload to prevent unsafe rendering assumptions | frontend unit | `cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx` | ✅ | ⬜ pending |
| 01-01-03 | 01 | 1 | INTENT-03, INTENT-04 | T-01-01, T-01-03 | Clarification loop helper behavior is test-enforced before orchestration work | unit/integration | `PYTHONPATH=. pytest src/tests/services/test_clarification_loop.py -x && cd web && npm test -- --runInBand --testPathPatterns=ClarificationFlow.test.tsx` | ✅ | ⬜ pending |
| 01-02-01 | 02 | 2 | INTENT-02, INTENT-03 | T-01-04, T-01-05 | Extraction includes weather/timeline/budget normalization with confidence + ambiguity thresholds | unit | `PYTHONPATH=. pytest src/tests/nlp/test_intent.py src/tests/nlp/test_intent_confidence.py -x` | ✅ | ⬜ pending |
| 01-02-02 | 02 | 2 | INTENT-03, INTENT-04 | T-01-04, T-01-05, T-01-06 | Iterative merge/update loop preserves prior constraints/history and returns one next question | service+api | `PYTHONPATH=. pytest src/tests/services/test_clarification_loop.py src/tests/api/test_search.py -x` | ✅ | ⬜ pending |
| 01-03-01 | 03 | 3 | INTENT-03, INTENT-04 | T-01-08, T-01-09 | One-question UI loop and recap chip editing flow stay guarded against repeat-submit and unsafe rendering | frontend integration | `cd web && npm test -- --runInBand --testPathPatterns=ClarificationFlow.test.tsx` | ✅ | ⬜ pending |
| 01-03-02 | 03 | 3 | INTENT-01, INTENT-04 | T-01-07, T-01-09 | Turn orchestration preserves session context across follow-up answers and recap edits | unit + e2e | `cd web && npm test -- --runInBand --testPathPatterns=Home.test.tsx && cd web && npx playwright test tests/e2e/clarification.spec.ts --project=chromium` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. Wave 0 test files are already planned in 01-01 and therefore not missing:

- `src/tests/services/test_clarification_loop.py`
- `src/tests/nlp/test_intent_confidence.py`
- `web/src/components/search/__tests__/ClarificationFlow.test.tsx`
- `web/tests/e2e/clarification.spec.ts`

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 240s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-25
