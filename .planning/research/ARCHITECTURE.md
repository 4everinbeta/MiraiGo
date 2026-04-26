# Architecture Integration: Realtime Airfare (Amadeus + Duffel)

**Project:** MiraiGo Travel Discovery  
**Scope:** Add flight-only realtime pricing context from two providers  
**Researched:** 2026-04-26

## Target Integration Shape

Current:

`SearchService -> Provider.search() -> FlightSearchResult -> ranking -> response`

Target:

`SearchService -> Provider adapters (Amadeus/Duffel) -> airfare normalizer -> unified airfare context -> ranking enrichment -> response`

## Integration Points

1. **Provider registry + orchestration**
   - `src/app/providers/registry.py`
   - `src/app/services/search.py`
   - Register and fan out to both flight providers.
2. **Provider adapter contract**
   - `src/app/providers/base.py`
   - Keep a common adapter interface.
3. **Normalization boundary (new)**
   - `src/app/services/airfare_normalization.py`
   - Convert provider payloads into one canonical airfare shape.
4. **Ranking integration**
   - `src/app/services/search.py`
   - Consume only normalized airfare fields.
5. **Response/schema contract**
   - `src/app/schemas/search.py`
   - `web/src/lib/api.ts`
   - Add freshness/provenance metadata fields.

## New Modules

- `src/app/providers/amadeus.py`
- `src/app/services/airfare_normalization.py`
- `src/app/schemas/airfare.py`
- tests for adapter and normalizer

## Existing Files Likely to Change

- `src/app/core/config.py` (Amadeus creds/base URL/TTL settings)
- `src/app/providers/registry.py`
- `src/app/services/search.py`
- `src/app/schemas/search.py`
- `web/src/lib/api.ts`
- `web/src/components/search/ResultsDashboard.tsx`

## Error-Handling Boundaries

1. Provider errors are isolated and categorized (auth/rate/timeout/upstream).
2. Bad single offers are dropped; provider response can still be partially valid.
3. Search response remains best-effort with explicit warnings/provider status.
4. Ranking falls back safely when airfare context is unavailable/stale.

## Incremental Build Order

1. Contracts/config
2. Amadeus adapter
3. Normalizer extraction (including Duffel normalization path)
4. Dual-provider fanout merge
5. Ranking enrichment
6. Frontend type/render updates
7. Hardening (rate-limit handling + metrics/alerts)

