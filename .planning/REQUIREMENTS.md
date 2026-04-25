# Requirements: MiraiGo Travel Discovery

**Defined:** 2026-04-24
**Core Value:** Given vague travel intent, MiraiGo reliably converts it into personalized, ranked destination suggestions with clear rationale.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Intent & Input

- [x] **INTENT-01**: User can submit a free-form natural-language travel prompt describing broad preferences.
- [x] **INTENT-02**: System can extract structured constraints from prompt (geography, weather, budget, timeline, trip length).
- [x] **INTENT-03**: System can detect missing critical constraints and ask focused clarifying follow-up questions.
- [x] **INTENT-04**: User can answer follow-up questions and update constraints without restarting search.

### Recommendations

- [ ] **RECO-01**: User receives a ranked list of destination suggestions based on current constraints.
- [ ] **RECO-02**: Each destination includes a clear explanation of why it fits user preferences.
- [ ] **RECO-03**: System surfaces alternative options when user constraints are conflicting or infeasible.

### Pricing & Budget

- [ ] **PRICE-01**: System integrates live flight pricing data for candidate destinations.
- [ ] **PRICE-02**: System integrates live hotel pricing data for candidate destinations.
- [ ] **PRICE-03**: Budget fit is computed from live pricing and shown per recommendation.
- [ ] **PRICE-04**: Recommendation output displays pricing freshness/provenance metadata.

### Discovery Controls

- [ ] **DISC-01**: User can filter recommendations by budget range.
- [ ] **DISC-02**: User can filter recommendations by travel date or flexible date window.
- [ ] **DISC-03**: User can filter recommendations by flight constraints (e.g., stops, duration).
- [ ] **DISC-04**: User can save destinations to a shortlist.
- [ ] **DISC-05**: User can share shortlist via a link.

### Global Coverage

- [ ] **GLOB-01**: Recommendation engine supports worldwide destination discovery.
- [ ] **GLOB-02**: System normalizes currency and location data across regions for consistent comparison.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Planning

- **PLAN-01**: User can generate a full day-by-day itinerary for selected destination.
- **PLAN-02**: User can receive adaptive itinerary updates based on weather or availability changes.

### Commerce & Conversion

- **COMM-01**: User can complete flight/hotel booking checkout directly in MiraiGo.
- **COMM-02**: User can receive price guarantees on quoted travel options.

### Advanced Personalization

- **PERS-01**: User can tune ranking tradeoffs interactively (cost vs weather vs travel time) with persistent preferences.
- **PERS-02**: User receives personalized recommendations based on prior sessions/history.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Full day-by-day itinerary generation in v1 | Dilutes core destination discovery objective and increases complexity early |
| In-product booking checkout in v1 | Adds payment/compliance complexity before core recommendation quality is validated |
| Price guarantee commitments in v1 | Introduces legal/operational risk before provider reliability is established |
| Social/community feed features | Not required to prove destination recommendation core value |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INTENT-01 | Phase 1 | Complete |
| INTENT-02 | Phase 1 | Complete |
| INTENT-03 | Phase 1 | Complete |
| INTENT-04 | Phase 1 | Complete |
| RECO-01 | Phase 2 | Pending |
| RECO-02 | Phase 2 | Pending |
| RECO-03 | Phase 2 | Pending |
| PRICE-01 | Phase 3 | Pending |
| PRICE-02 | Phase 3 | Pending |
| PRICE-03 | Phase 3 | Pending |
| PRICE-04 | Phase 3 | Pending |
| DISC-01 | Phase 4 | Pending |
| DISC-02 | Phase 4 | Pending |
| DISC-03 | Phase 4 | Pending |
| DISC-04 | Phase 5 | Pending |
| DISC-05 | Phase 5 | Pending |
| GLOB-01 | Phase 2 | Pending |
| GLOB-02 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-24*
*Last updated: 2026-04-24 after roadmap mapping*
