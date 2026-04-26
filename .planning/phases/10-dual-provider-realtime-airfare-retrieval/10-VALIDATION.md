---
phase: 10
slug: dual-provider-realtime-airfare-retrieval
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-26
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `src/tests/conftest.py` |
| **Quick run command** | `./venv/bin/pytest src/tests/providers/test_duffel.py -q` |
| **Full suite command** | `./venv/bin/pytest src/tests/providers/test_duffel.py src/tests/providers/test_amadeus.py src/tests/services/test_search_dual_provider.py -q` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every task commit:** run quick command for touched tests.
- **After every plan wave:** run full suite command.
- **Before `/gsd-verify-work`:** full suite must be green.
- **Max feedback latency:** 180 seconds.

---

## Per-Task Verification Map

| Requirement | Behavior | Test Type | Automated Command | File Exists |
|-------------|----------|-----------|-------------------|-------------|
| AIR-01 | Amadeus adapter returns mapped flight results | unit | `./venv/bin/pytest src/tests/providers/test_amadeus.py::test_amadeus_provider_builds_flight_results -q` | ❌ |
| AIR-01 | Amadeus refreshes token once on 401 | unit | `./venv/bin/pytest src/tests/providers/test_amadeus.py::test_amadeus_refreshes_token_once_on_401 -q` | ❌ |
| AIR-02 | Duffel still returns mapped flight results in dual-provider mode | unit | `./venv/bin/pytest src/tests/providers/test_duffel.py -q` | ✅ |
| AIR-01, AIR-02 | Deterministic provider-tagged interleave ordering | integration | `./venv/bin/pytest src/tests/services/test_search_dual_provider.py::test_dual_provider_interleave_is_deterministic -q` | ❌ |
| AIR-01, AIR-02 | Partial-provider failure keeps available results + warning/status | integration | `./venv/bin/pytest src/tests/services/test_search_dual_provider.py::test_partial_failure_returns_other_provider_results -q` | ❌ |

---

## Wave 0 Requirements

- [ ] Create `src/tests/providers/test_amadeus.py`.
- [ ] Create `src/tests/services/test_search_dual_provider.py`.
- [ ] Add provider timeout/auth failure fixtures for deterministic dual-provider scenarios.

---

## Manual-Only Verifications

| Behavior | Why Manual | Test Instructions |
|----------|------------|-------------------|
| Provider degraded-state messaging is understandable | UX clarity judgment | Force one provider failure and verify warning/status language is explicit and non-silent |

---

## Validation Sign-Off

- [ ] All tasks include executable verification commands.
- [ ] Wave 0 gaps are closed.
- [ ] Sampling continuity maintained.
- [ ] `nyquist_compliant` can be promoted to true after Phase 10 execution evidence.

**Approval:** pending

