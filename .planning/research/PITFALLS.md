# Domain Pitfalls — Realtime Airfare Integration (Amadeus + Duffel)

**Domain:** Flight-only realtime pricing context for discovery  
**Researched:** 2026-04-26

## Critical Pitfalls

1. **Schema drift across providers/versions**
   - Mitigation: contract-first canonical schema + adapter contract tests + unknown-field telemetry.
2. **Stale/expired pricing shown as current**
   - Mitigation: freshness policy, expiry checks, repricing gate, visible freshness labels.
3. **Currency/tax/fee mismatch**
   - Mitigation: canonical monetary model + explicit comparison rules + parity tests.
4. **Partial outage handling failures**
   - Mitigation: provider-isolated timeout/circuit-breaker behavior + partial success contract.
5. **Rate-limit bursts from clarification loops**
   - Mitigation: dedupe keys, short cache, request coalescing, rate-aware backoff.
6. **Async/partial result handling mistakes**
   - Mitigation: result state markers (`partial|complete|timed_out`) and late-offer rerank policy.

## Moderate Pitfalls

1. Ranking polluted by non-equivalent fare products (baggage/refund differences).
2. Missing provenance/freshness in UI reducing trust.

## Minor Pitfalls

1. Timezone/date-boundary bugs.
2. Currency rounding drift.

## Phase Mapping Guidance

- **Phase for provider/normalization core:** schema, freshness, currency rules, resiliency.
- **Phase for ranking:** comparable fare-quality-aware scoring.
- **Phase for filters/UI:** only normalized current totals; preserve provenance/freshness.

