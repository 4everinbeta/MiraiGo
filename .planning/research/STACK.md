# Technology Stack — Realtime Airfare (Amadeus + Duffel)

**Project:** MiraiGo Travel Discovery (v1.1 flight-only realtime airfare)  
**Researched:** 2026-04-26

## Recommended Stack Changes

1. Keep `httpx` and existing provider abstraction; add `AmadeusFlightsProvider` and harden `DuffelFlightsProvider`.
2. Add `tenacity` for explicit retry/backoff policies.
3. Extend Redis usage for token cache, provider-aware response cache, and distributed outbound rate buckets.
4. Add observability: `prometheus-fastapi-instrumentator` and `python-json-logger`.

## Provider/API Notes

### Amadeus
- OAuth token endpoint (`client_credentials`) with short token lifecycle.
- Flight offers search/pricing endpoints.
- Implement token cache with safety buffer and single-flight refresh lock.

### Duffel
- Static bearer token + required `Duffel-Version: v2`.
- Offer request endpoint with `supplier_timeout`.
- Respect 429 headers (`ratelimit-*`) for backoff.

## Runtime Policy

### Rate limiting
- Redis-backed provider-specific limiter:
  - `provider:amadeus` bucket (TPS caps by env)
  - `provider:duffel` adaptive bucket from response headers

### Retry and timeout
- Retry only network/timeout/429/503/504.
- Do not retry validation/state 4xx.
- Keep fan-out bounded so one provider does not block whole response.

### Caching
- Replace long generic search cache for airfare with short provider caches:
  - `FLIGHT_PROVIDER_CACHE_TTL_SECONDS=60..120`
  - `FLIGHT_EMPTY_RESULT_TTL_SECONDS=15..30`
  - `SEARCH_RESPONSE_TTL_SECONDS=60..120`
- Emit freshness/provenance metadata in normalized output.

## Required Config Deltas

- `AMADEUS_BASE_URL`
- `AMADEUS_CLIENT_ID`
- `AMADEUS_CLIENT_SECRET`
- `DUFFEL_ACCESS_TOKEN`
- `DUFFEL_API_VERSION` (default `v2`)
- Flight cache TTL keys above

## What Not to Add in v1.1

- Booking/order flows
- Webhooks
- Queue/worker platform expansion
- New API gateway/service mesh
- Hotel integration

