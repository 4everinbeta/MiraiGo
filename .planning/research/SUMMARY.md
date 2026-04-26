# Milestone v1.1 Research Summary — Realtime Airfare Integrations

**Scope:** Flight-only realtime airfare integrations using Amadeus + Duffel.

## Stack additions

- Keep existing FastAPI/provider architecture and `httpx`.
- Add `tenacity` for retry policy clarity.
- Extend Redis for token/cache/rate-bucket logic.
- Add structured metrics/logging for provider reliability visibility.

## Feature table stakes

1. Dual-provider realtime retrieval.
2. Canonical normalization for comparability.
3. Freshness/provenance metadata in responses.
4. Partial-failure resilience.
5. Ranking integration with airfare context.

## Watch out for

- Provider schema/version drift.
- Stale/expired fares presented as current.
- Currency/tax inconsistencies causing bad ranking/filter behavior.
- Clarification-loop traffic causing rate-limit/cost spikes.

## Recommended execution order

1. Define contracts/config.
2. Implement Amadeus provider.
3. Add normalization boundary and route Duffel through it.
4. Enable dual-provider merge/fanout.
5. Enrich ranking + API/frontend metadata.
6. Harden with retries, rate-limits, caching, and observability.

