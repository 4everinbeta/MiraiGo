# Roadmap: MiraiGo Travel Discovery

## Milestones

- ✅ **v1.0 Intent Clarification Foundation** — shipped 2026-04-26 ([roadmap archive](.planning/milestones/v1.0-ROADMAP.md), [requirements archive](.planning/milestones/v1.0-REQUIREMENTS.md), [audit](.planning/milestones/v1.0-MILESTONE-AUDIT.md), [phase artifacts](.planning/milestones/v1.0-phases/))
- 🚧 **v1.1 Realtime Airfare Integrations** — roadmap created

## Active Milestone (v1.1 Realtime Airfare Integrations)

## Phases

- [x] **Phase 10: Dual-Provider Realtime Airfare Retrieval** - Users can receive live airfare offers from Amadeus and Duffel for their current travel constraints.
- [x] **Phase 11: Airfare Normalization, Provenance, and Contracts** - Users can compare cross-provider airfare results with consistent fields and metadata.
- [ ] **Phase 12: Degraded-Mode Reliability and Clarification Continuity** - Users still get useful airfare results and keep resolved intent when a provider degrades.
- [ ] **Phase 13: Ranking with Live Airfare Context** - Destination ranking and budget-fit use normalized realtime airfare totals.

## Phase Details

### Phase 10: Dual-Provider Realtime Airfare Retrieval
**Goal**: Users can receive live airfare offers from both Amadeus and Duffel during discovery.
**Depends on**: Phase 9
**Requirements**: AIR-01, AIR-02
**Success Criteria** (what must be TRUE):
  1. User can run discovery with selected constraints and receive realtime flight offers sourced from Amadeus.
  2. User can run discovery with selected constraints and receive realtime flight offers sourced from Duffel.
  3. User sees airfare results returned in the same discovery flow without needing a separate flight lookup step.
**Plans**: 10-01, 10-02, 10-03
**UI hint**: yes

### Phase 11: Airfare Normalization, Provenance, and Contracts
**Goal**: Users can compare airfare results consistently across providers with deterministic payload shape.
**Depends on**: Phase 10
**Requirements**: AIR-03, AIR-04, AIR-08
**Success Criteria** (what must be TRUE):
  1. User can view comparable normalized airfare fields (price, currency, stops, duration) across Amadeus and Duffel offers.
  2. User can view freshness and provenance metadata for each airfare offer.
  3. User sees stable airfare rendering/behavior across refreshes and turns because airfare-context fields are deterministic.
**Plans**: 10 plans
Plans:
- [x] 11-01-PLAN.md — Define backend normalized/provenance airfare contracts and deterministic helper utilities.
- [x] 11-02-PLAN.md — Wire provider/service normalization with deterministic API payload behavior.
- [x] 11-03-PLAN.md — Mirror contracts in frontend and render normalized/provenance UI deterministically.
- [x] 11-04-PLAN.md — Close clarification completion/flight gating mismatch with shared prerequisite contract and Continue guard.
- [x] 11-05-PLAN.md — Add explicit flight-metadata absence remediation in results experience.
- [x] 11-06-PLAN.md — Close origin-entry dead-end by adding explicit origin capture control and contract-aligned turn updates.
- [x] 11-07-PLAN.md — Close blocked Continue date-range dead-end with direct remediation controls and deterministic unblock regressions.
- [x] 11-08-PLAN.md — Close no-flight empty-state clarity gap with deterministic cause-specific remediation guidance.
- [x] 11-09-PLAN.md — Close airfare intent-capture/progression gap for natural prompts with tests-first deterministic remediation flow.
- [ ] 11-10-PLAN.md — Close low-detail airfare prompt burden with minimum-detail clarification progression and typed remediation sequencing.
**UI hint**: yes

### Phase 12: Degraded-Mode Reliability and Clarification Continuity
**Goal**: Users continue receiving airfare context and keep conversation continuity even during provider degradation.
**Depends on**: Phase 11
**Requirements**: AIR-05, AIR-06
**Success Criteria** (what must be TRUE):
  1. If one provider is degraded, user still receives flight results from available sources.
  2. When degraded mode is active, user sees explicit degraded-state signaling in results.
  3. User can answer/edit/continue clarification turns without losing previously resolved intent while airfare updates are applied.
**Plans**: 1 plan
Plans:
- [ ] 12-01-PLAN.md — Implement degraded-mode reliability and clarification continuity contracts for AIR-05/AIR-06.
**UI hint**: yes

### Phase 13: Ranking with Live Airfare Context
**Goal**: Users get destination ranking and budget-fit outputs that reflect normalized current airfare totals.
**Depends on**: Phase 12
**Requirements**: AIR-07
**Success Criteria** (what must be TRUE):
  1. User-facing destination ranking reflects normalized current airfare totals.
  2. User-facing budget-fit output updates when airfare totals change.
**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 10. Dual-Provider Realtime Airfare Retrieval | 3/3 | Complete | 2026-04-26 |
| 11. Airfare Normalization, Provenance, and Contracts | 9/9 | Complete    | 2026-05-24 |
| 12. Degraded-Mode Reliability and Clarification Continuity | 0/1 | Not started | - |
| 13. Ranking with Live Airfare Context | 0/0 | Not started | - |
