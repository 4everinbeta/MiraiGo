# Phase 10: Dual-Provider Realtime Airfare Retrieval - Research

**Researched:** 2026-04-26  
**Domain:** FastAPI provider fan-out for live dual-flight retrieval (Amadeus + Duffel)  
**Confidence:** MEDIUM

## User Constraints (from CONTEXT.md)

- Hybrid trigger policy with bounded prefetch and strict visible gate (D10-01..D10-03).
- Best-effort partial success + explicit warning/status signaling (D10-04..D10-06).
- Deterministic provider-tagged merge ordering (D10-07..D10-08).
- Amadeus OAuth token cache in Redis with single refresh-on-401; Duffel static token with explicit misconfig signal (D10-09..D10-11).

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AIR-01 | Realtime Amadeus flight offers | Add `AmadeusFlightsProvider` adapter, OAuth token manager, registry wiring, deadline-bounded execution |
| AIR-02 | Realtime Duffel flight offers | Preserve/extend existing `DuffelFlightsProvider` path in dual-provider fan-out |

## Concrete Implementation Approach (Phase 10)

1. Add `src/app/providers/amadeus.py` implementing `TravelProvider`:
   - OAuth token request (`client_credentials`) and Redis-backed token cache.
   - Flight offers request mapping into existing `FlightSearchResult` contract.
2. Update `src/app/providers/registry.py` to register both `AmadeusFlightsProvider()` and `DuffelFlightsProvider()` for `InventoryType.FLIGHT`.
3. Extend `SearchService.search()` / execution path:
   - Enforce visible retrieval gate: origin + destination + date range + stable clarification turn.
   - Allow prefetch only when destination + timeline are known.
   - Apply per-provider hard deadline and preserve partial-success responses.
4. Replace pure global-sort behavior for dual-provider retrieval with deterministic provider-tagged interleave for this phase’s output.

## Architectural Patterns

### Provider adapter + shared request primitive
- Keep transport concerns in provider classes; reuse shared `TravelProvider.request()` error model.

### Hybrid retrieval gate
- Separate prefetch eligibility from visible retrieval eligibility.

### Deterministic interleave merge
- Preserve each provider’s internal order, interleave by head score, and retain provider source tags.

## Common Pitfalls

1. Cache-key fragmentation across clarification turns if prefetch key includes unstable turn metadata.
2. Deadline inversion between provider timeout and upstream supplier timeout.
3. Silent degradation when one provider fails but no warning/status reason is emitted.

## Minimal Schema/Config Changes (Phase 10 Only)

### Config additions
- `AMADEUS_API_URL`
- `AMADEUS_CLIENT_ID`
- `AMADEUS_CLIENT_SECRET`
- `AMADEUS_TOKEN_SAFETY_BUFFER_SECONDS`
- Per-provider deadline/timeout config keys
- Prefetch TTL key for flight retrieval cache

### Schema strategy
- Prefer no new public response contract fields in Phase 10; reuse existing `results[].provider`, `provider_status[].reason`, and `warnings[]`.
- Full canonical normalization is deferred to Phase 11.

## Validation Architecture

### Test framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (project venv) |
| Quick run command | `./venv/bin/pytest src/tests/providers/test_amadeus.py src/tests/services/test_search_dual_provider.py -q` |
| Full suite command | `./venv/bin/pytest -q` |

### Phase requirements → test map

| Req ID | Behavior | Test Type | Automated Command | File Exists |
|--------|----------|-----------|-------------------|-------------|
| AIR-01 | Amadeus provider maps offers to `FlightSearchResult` | unit | `./venv/bin/pytest src/tests/providers/test_amadeus.py::test_amadeus_provider_builds_flight_results -q` | ❌ Wave 0 |
| AIR-01 | 401 triggers one refresh + one retry | unit | `./venv/bin/pytest src/tests/providers/test_amadeus.py::test_amadeus_refreshes_token_once_on_401 -q` | ❌ Wave 0 |
| AIR-02 | Duffel path remains valid in dual-provider run | unit/integration | `./venv/bin/pytest src/tests/providers/test_duffel.py -q` | ✅ |
| AIR-01/AIR-02 | Deterministic interleave and provider tagging | integration | `./venv/bin/pytest src/tests/services/test_search_dual_provider.py::test_dual_provider_interleave_is_deterministic -q` | ❌ Wave 0 |
| AIR-01/AIR-02 | Partial failure still returns available provider results + warnings | integration | `./venv/bin/pytest src/tests/services/test_search_dual_provider.py::test_partial_failure_returns_other_provider_results -q` | ❌ Wave 0 |

### Wave 0 gaps
- Create `src/tests/providers/test_amadeus.py`.
- Create `src/tests/services/test_search_dual_provider.py`.
- Add provider timeout/failure fixtures for dual-provider execution.

## Security Threat Model Inputs

### Applicable controls
- Credential handling for provider tokens/secrets.
- Input validation bounds already enforced by `SearchRequest`.
- Outbound request hardening via trusted base URLs and bounded retries/timeouts.

### Threat patterns
1. Token leakage in logs/errors.
2. Retry storms on auth/rate-limit failures.
3. Outbound request misuse if base URLs become user-controlled.
4. Input-driven request amplification.

### Required mitigations in this phase
- Never log provider auth headers/tokens.
- Keep bounded retry policy and single forced token refresh on 401.
- Keep provider base URLs config-controlled only.
- Preserve request validation limits (`limit_per_provider`, traveler/date bounds).

## Sources

- Internal codebase:
  - `src/app/services/search.py`
  - `src/app/providers/base.py`
  - `src/app/providers/duffel.py`
  - `src/app/providers/registry.py`
  - `src/app/schemas/search.py`
  - `src/app/core/config.py`
- Planning context:
  - `.planning/phases/10-dual-provider-realtime-airfare-retrieval/10-CONTEXT.md`
  - `.planning/REQUIREMENTS.md`
  - `.planning/ROADMAP.md`
- External references:
  - Amadeus OAuth/flight APIs (developer guides + OpenAPI)
  - Duffel offer request/response handling docs
  - Python asyncio timeout semantics
  - RFC 6749 OAuth2 client credentials

## RESEARCH COMPLETE

### Key Findings
- Existing architecture cleanly supports adding Amadeus as a provider adapter.
- Phase 10 must prioritize retrieval reliability and deterministic merging over full normalization.
- Shared Redis token caching is required for Amadeus auth correctness in multi-instance scenarios.

### Ready for Planning
- Research complete. Planner can produce executable Phase 10 plans.

