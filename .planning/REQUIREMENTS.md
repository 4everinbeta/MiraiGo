# Requirements: MiraiGo Travel Discovery

**Defined:** 2026-04-26  
**Core Value:** Given vague travel intent, MiraiGo reliably converts it into personalized, ranked destination suggestions with clear rationale.

## v1.1 Requirements

### Realtime Airfare Providers

- [x] **AIR-01
**: User can receive realtime flight offers from Amadeus for selected travel constraints.
- [x] **AIR-02
**: User can receive realtime flight offers from Duffel for selected travel constraints.
- [x] **AIR-03
**: User can view comparable normalized airfare fields (price, currency, stops, duration) across providers.
- [x] **AIR-04
**: User can view freshness and provenance metadata for each airfare offer.

### Reliability & Continuity

- [x] **AIR-05
**: User can still receive flight results when one provider is degraded, with explicit degraded-state signaling.
- [x] **AIR-06
**: User can continue clarification/edit/continue flows without losing previously resolved intent while airfare updates are applied.

### Ranking & Contract Integrity

- [ ] **AIR-07**: User-facing ranking and budget-fit calculations use normalized current airfare totals.
- [x] **AIR-08
**: API and frontend contracts expose deterministic typed airfare-context fields for rendering and logic.

## v2 Requirements

Deferred beyond this milestone.

### Expanded Commerce & Inventory

- **AIRX-01**: User can proceed from discovery offers to booking/checkout flows.
- **AIRX-02**: User can compare realtime hotel pricing in the same recommendation loop.
- **AIRX-03**: User can receive proactive fare-watch alerts and reprice notifications.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Booking checkout/ticketing | Changes milestone from discovery to commerce and expands risk significantly |
| Hotel provider integration | Explicitly deferred to keep v1.1 flight-only and ship quickly |
| Price guarantees | High volatility and legal/trust risk for first realtime milestone |
| Complex fare optimization hacks | High complexity with poor trust/maintainability payoff for v1.1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AIR-01 | Phase 10 | Completed |
| AIR-02 | Phase 10 | Completed |
| AIR-03 | Phase 11 | Completed |
| AIR-04 | Phase 11 | Completed |
| AIR-05 | Phase 12 | Completed |
| AIR-06 | Phase 12 | Completed |
| AIR-07 | Phase 13 | Pending |
| AIR-08 | Phase 11 | Completed |

**Coverage:**
- v1.1 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0 ✅

---
*Requirements defined: 2026-04-26*  
*Last updated: 2026-04-26 after milestone v1.1 roadmap mapping*
