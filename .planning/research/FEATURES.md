# Feature Landscape: Realtime Airfare Providers (Amadeus + Duffel) — v1.1

**Domain:** Travel discovery (flight-only realtime pricing context)  
**Researched:** 2026-04-26

## Table Stakes (must-have)

1. Dual-provider live quote retrieval (Amadeus + Duffel).
2. Unified airfare normalization schema for cross-provider comparability.
3. Price freshness/provenance on each offer.
4. Graceful partial-failure behavior (one provider down != empty results).
5. Budget-fit/ranking integration that uses airfare context.
6. Clarification continuity preserved while pricing updates.

## Differentiators (secondary in this milestone)

1. Cross-provider “best fare” explanation.
2. Price confidence states (fresh/aging/stale).
3. Smart refresh triggers on meaningful intent edits.
4. Budget transparency messaging tied to airfare share.

## Anti-Features (out of scope)

1. Booking/checkout flows.
2. Hotel integrations.
3. Guaranteed-price claims.
4. Advanced fare optimization hacks.
5. Hard dependency on both providers succeeding every request.

## Dependency Sequence

1. Provider adapters  
2. Canonical normalization + provenance  
3. Merge + ranking ingestion  
4. UI transparency  
5. Optional differentiators

