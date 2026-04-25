# Roadmap: MiraiGo Travel Discovery

## Overview

MiraiGo v1 delivers a complete destination discovery flow: users start with a free-form travel prompt, refine intent through clarifying questions, receive globally scoped ranked recommendations with transparent rationale, see live pricing-backed budget fit, then narrow and share a shortlist for decision-making.

## Phases

- [ ] **Phase 1: Intent Capture & Clarification** - Turn vague travel prompts into complete, actionable constraints.
- [ ] **Phase 2: Global Recommendation Engine** - Deliver ranked destination options with clear fit explanations and feasible alternatives.
- [ ] **Phase 3: Live Pricing & Budget Trust** - Enrich recommendations with real-time flight/hotel pricing and transparent freshness metadata.
- [ ] **Phase 4: Discovery Filters** - Let users refine recommendation results with practical travel filters.
- [ ] **Phase 5: Shortlist Save & Share** - Enable users to save promising destinations and share their shortlist by link.
- [x] **Phase 6: Fix intent extraction for timeline and destination parsing** - Improve extraction reliability for destination/timeline constraints.
- [ ] **Phase 7: Enhanced NLP** - Improve search-intent NLP breadth, precision, and robustness for real-world phrasing.
- [ ] **Phase 8: Intent Verification Closure** - Close unresolved INTENT requirement verification gaps from milestone audit.
- [ ] **Phase 9: Milestone Integration & Validation Backfill** - Close cross-phase integration and missing validation artifacts before milestone completion.

## Phase Details

### Phase 1: Intent Capture & Clarification
**Goal**: Users can express travel intent naturally and iteratively complete missing constraints without restarting.
**Depends on**: Nothing (first phase)
**Requirements**: INTENT-01, INTENT-02, INTENT-03, INTENT-04
**Success Criteria** (what must be TRUE):
  1. User can submit a free-form natural-language travel prompt and start a search.
  2. System extracts and retains core constraints from the prompt (geography, weather, budget, timeline, trip length).
  3. System asks focused follow-up questions when critical constraints are missing.
  4. User can answer follow-up questions and continue the same search with updated constraints.
**Plans**: 3 plans
Plans:
- [ ] 01-01-PLAN.md — Define clarification contracts, dependency graph constants, and Wave 0 tests
- [ ] 01-02-PLAN.md — Implement confidence-aware extraction and backend iterative clarification orchestration
- [ ] 01-03-PLAN.md — Implement inline clarification UX, recap chip edits, and end-to-end turn wiring
**UI hint**: yes

### Phase 2: Global Recommendation Engine
**Goal**: Users can receive globally scoped, ranked destination recommendations with clear rationale, even when initial constraints conflict.
**Depends on**: Phase 1
**Requirements**: RECO-01, RECO-02, RECO-03, GLOB-01
**Success Criteria** (what must be TRUE):
  1. User receives a ranked list of destination suggestions based on current constraints.
  2. Each suggested destination includes a clear explanation of why it matches user preferences.
  3. When constraints are conflicting or infeasible, system surfaces feasible alternative destinations.
  4. Recommendations can include destinations worldwide rather than being limited to a subset of regions.
**Plans**: TBD

### Phase 3: Live Pricing & Budget Trust
**Goal**: Users can evaluate recommendations with live pricing context and trust how fresh and comparable the budget information is.
**Depends on**: Phase 2
**Requirements**: PRICE-01, PRICE-02, PRICE-03, PRICE-04, GLOB-02
**Success Criteria** (what must be TRUE):
  1. User can see live flight pricing context for recommended destinations.
  2. User can see live hotel pricing context for recommended destinations.
  3. Each recommendation shows computed budget fit based on live flight and hotel pricing data.
  4. Recommendation output shows pricing source and freshness/provenance metadata.
  5. Pricing and location values are normalized across regions so users can compare destinations consistently.
**Plans**: TBD

### Phase 4: Discovery Filters
**Goal**: Users can narrow recommendation results quickly using practical travel constraints.
**Depends on**: Phase 3
**Requirements**: DISC-01, DISC-02, DISC-03
**Success Criteria** (what must be TRUE):
  1. User can filter recommendations by budget range and see results update accordingly.
  2. User can filter recommendations by travel date or flexible date window.
  3. User can filter recommendations by flight constraints such as stops or duration.
**Plans**: TBD
**UI hint**: yes

### Phase 5: Shortlist Save & Share
**Goal**: Users can persist preferred destinations and share decision options with others.
**Depends on**: Phase 4
**Requirements**: DISC-04, DISC-05
**Success Criteria** (what must be TRUE):
  1. User can save recommended destinations into a personal shortlist during discovery.
  2. User can revisit saved destinations within the shortlist experience.
  3. User can generate and share a link to the shortlist with others.
**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Intent Capture & Clarification | 0/TBD | Not started | - |
| 2. Global Recommendation Engine | 0/TBD | Not started | - |
| 3. Live Pricing & Budget Trust | 0/TBD | Not started | - |
| 4. Discovery Filters | 0/TBD | Not started | - |
| 5. Shortlist Save & Share | 0/TBD | Not started | - |
| 6. Fix intent extraction for timeline and destination parsing | 1/1 | Complete | 06-01-PLAN.md |
| 7. Enhanced NLP | 0/TBD | Not started | - |
| 8. Intent Verification Closure | 0/TBD | Not started | - |
| 9. Milestone Integration & Validation Backfill | 0/TBD | Not started | - |

### Phase 6: Fix intent extraction for timeline and destination parsing

**Goal:** Improve extraction reliability so timeline and destination slots remain accurate and clarification-safe across ambiguous natural-language phrasing.
**Requirements**: INTENT-02, INTENT-03, INTENT-04
**Depends on:** Phase 1
**Plans:** 1 plan

Plans:
- [x] 06-01-PLAN.md — Harden destination/timeline parsing semantics, add edge-case tests, and verify clarification compatibility

### Phase 7: Enhanced NLP

**Goal:** Enhance the natural language processing for the search intent.
**Requirements**: INTENT-02, INTENT-03, INTENT-04
**Depends on:** Phase 6
**Plans:** 3 plans

Plans:
- [ ] 07-01-PLAN.md — Accuracy and ambiguity hardening for core extraction
- [ ] 07-02-PLAN.md — Multilingual query support and language-aware normalization
- [ ] 07-03-PLAN.md — Synonym expansion and robustness tuning

### Phase 8: Intent Verification Closure

**Goal:** Close unresolved verification debt for INTENT-01 through INTENT-04 and bring Phase 1 acceptance evidence to a fully verified state.
**Requirements**: INTENT-01, INTENT-02, INTENT-03, INTENT-04
**Depends on:** Phase 7
**Gap Closure:** Closes requirement gaps from milestone audit (`v1.0-v1.0-MILESTONE-AUDIT.md`)
**Plans:** TBD

### Phase 9: Milestone Integration & Validation Backfill

**Goal:** Complete missing cross-phase integration checks, close milestone E2E flow audit gaps, and backfill missing Nyquist validation artifacts.
**Requirements**: INTENT-01, INTENT-02, INTENT-03, INTENT-04
**Depends on:** Phase 8
**Gap Closure:** Closes integration/flow/Nyquist gaps from milestone audit (`v1.0-v1.0-MILESTONE-AUDIT.md`)
**Plans:** TBD
