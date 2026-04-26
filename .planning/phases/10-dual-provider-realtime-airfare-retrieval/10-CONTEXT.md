# Phase 10: Dual-Provider Realtime Airfare Retrieval - Context

**Gathered:** 2026-04-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver dual-provider realtime airfare retrieval in the existing search flow so users can receive flight offers from both Amadeus and Duffel without introducing booking/hotel scope.

</domain>

<decisions>
## Implementation Decisions

### Provider-call trigger policy
- **D10-01:** Use a hybrid trigger policy.
- **D10-02:** Prefetch is allowed only once destination + timeline are known.
- **D10-03:** User-visible realtime results require strict gating (origin + destination + date range resolved, and turn clarification state stable).

### Failure behavior and deadlines
- **D10-04:** Use best-effort partial success — return available provider results when one provider fails.
- **D10-05:** Surface explicit provider failure signaling via warnings/status metadata (no silent fail).
- **D10-06:** Enforce per-provider hard deadlines so a slow provider cannot block the turn.

### Source selection and merge policy
- **D10-07:** Keep provider attribution explicit and merge into one provider-tagged list.
- **D10-08:** Use deterministic merged ordering: preserve per-provider internal order, then interleave by current score while keeping source tags.

### Auth/token lifecycle policy
- **D10-09:** Amadeus uses cached OAuth token with safety buffer and single forced refresh on first 401.
- **D10-10:** Duffel remains static-token based; misconfiguration must be explicit in status/warnings.
- **D10-11:** Amadeus token cache is Redis-backed (shared), not process-local only.

### the agent's Discretion
- Exact timeout values and retry counts per provider (within phase goals).
- Concrete Redis key names and cache invalidation mechanics for token/prefetch storage.
- Final implementation shape for interleave helper, as long as deterministic behavior is preserved.

</decisions>

<specifics>
## Specific Ideas

- Reuse existing provider adapter pattern and service-centered orchestration; avoid bypassing `SearchService`.
- Keep this phase focused on retrieval and resilient fan-out; full normalization/detail shaping belongs to Phase 11.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase and requirement definitions
- `.planning/ROADMAP.md` — Phase 10 goal, dependencies, and success criteria.
- `.planning/REQUIREMENTS.md` — AIR-01 and AIR-02 definitions + traceability expectations.
- `.planning/PROJECT.md` — v1.1 milestone goal and out-of-scope constraints.
- `.planning/STATE.md` — current milestone status and sequencing.

### Research constraints for this phase
- `.planning/research/SUMMARY.md` — milestone-level integration order and risk priorities.
- `.planning/research/STACK.md` — provider auth/rate/caching/timeout guidance.
- `.planning/research/ARCHITECTURE.md` — integration boundaries and module touchpoints.
- `.planning/research/PITFALLS.md` — failure modes and prevention requirements relevant to retrieval.

### Existing implementation touchpoints
- `src/app/services/search.py` — orchestration/fan-out, warning handling, ranking entrypoint.
- `src/app/providers/base.py` — provider contract and request/retry primitives.
- `src/app/providers/duffel.py` — current flight provider behavior to preserve/extend.
- `src/app/providers/registry.py` — provider registration integration point.
- `src/app/schemas/search.py` — request/response and provider status contracts.
- `web/src/lib/api.ts` — frontend contract mirror for provider status/warnings/results.

### Prior phase decisions to preserve
- `.planning/milestones/v1.0-phases/01-intent-capture-clarification/01-CONTEXT.md` — clarification continuity and one-question-at-a-time flow assumptions.
- `.planning/milestones/v1.0-phases/09-milestone-integration-validation-backfill/09-CONTEXT.md` — backend schema canonicality and frontend contract alignment discipline.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `SearchService` provider fan-out + warning emission pipeline can be extended for dual-provider retrieval.
- Existing `DuffelFlightsProvider` provides the baseline adapter pattern for flight inventory.
- `ProviderStatus` + warning surfaces already exist to communicate degraded states.

### Established Patterns
- Thin API route + service orchestration pattern is established; avoid route-level provider logic.
- Provider adapters are the extension point for external travel APIs.
- Contract mirroring between backend schemas and `web/src/lib/api.ts` is expected and enforced.

### Integration Points
- Add `AmadeusFlightsProvider` and wire into `get_provider_registry()`.
- Extend `SearchService.search()` provider execution paths while preserving clarification gate behavior.
- Emit explicit status/warning signals for partial-provider failures.

</code_context>

<deferred>
## Deferred Ideas

- Full cross-provider normalization and canonical contract hardening (Phase 11).
- Ranking and budget-fit weighting with live airfare totals (Phase 13).
- Hotel integration and booking/checkout flows (out of scope for v1.1).

</deferred>

---

*Phase: 10-dual-provider-realtime-airfare-retrieval*
*Context gathered: 2026-04-26*
