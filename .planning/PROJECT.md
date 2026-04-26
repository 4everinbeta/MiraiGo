# MiraiGo Travel Discovery

## Current State

- **Shipped milestone:** v1.0 (2026-04-26)
- **Delivered:** End-to-end natural-language intent clarification with deterministic follow-up turns and continuity across answer/edit/continue flows.
- **Verification posture:** INTENT-01..04 closed with automated + human evidence; milestone audit closed as `tech_debt` (non-blocking items only).

## Next Milestone Goals

- Deliver ranked recommendation quality and rationale (RECO-01..03, GLOB-01).
- Add live pricing and budget trust features (PRICE-01..04, GLOB-02).
- Add discovery filters and shortlist save/share flow (DISC-01..05).

## What This Is

MiraiGo Travel Discovery is a travel planning website for leisure travelers that turns loose natural-language prompts into ranked destination suggestions. Users can describe broad preferences, and MiraiGo asks targeted follow-up questions when details are missing. The result is a guided, conversational way to narrow travel options by geography, weather, budget, and timeline.

## Core Value

Given vague travel intent, MiraiGo reliably converts it into personalized, ranked destination suggestions with clear rationale.

## Requirements

### Validated

- INTENT-01..04 validated and shipped in milestone v1.0.

### Active

- [ ] User can enter free-form natural-language travel prompts and receive ranked destination suggestions.
- [ ] MiraiGo can detect missing constraints and guide users with focused follow-up questions (geography, weather, costs, timelines).
- [ ] Suggestions include explanation of fit for user preferences.
- [ ] Budget support includes live real-time pricing integration for flights/hotels.
- [ ] Destination discovery supports worldwide coverage.

### Out of Scope

- Full day-by-day itinerary generation — keep v1 focused on destination discovery quality.
- Travel booking checkout flow — pricing context is needed, but booking transactions are not required for v1.

## Context

The existing repository already includes backend NLP and optimization modules, multiple verification scripts, and a web frontend foundation suitable for iterative feature expansion. The product direction centers on natural-language travel intent parsing and interactive clarification when prompts are underspecified. Key user intent dimensions include location preferences, climate/seasonality, trip length, and budget realism.

## Constraints

- **Product Scope**: v1 must prioritize ranked destination suggestions over itinerary generation — preserve focus and reduce delivery risk.
- **Coverage**: Suggestions must support global destinations from day one — users should not encounter region lock-in.
- **Data Freshness**: Budget recommendations require live pricing integrations — static cost bands are insufficient for expected behavior.
- **Interaction Model**: Input must remain natural-language-first — avoid forcing rigid forms before initial suggestion generation.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Target leisure travelers first | Most direct alignment with stated use case and simplified persona assumptions | Active |
| v1 output is ranked destinations with rationale | Delivers immediate value without overextending into itinerary complexity | In progress (v1.1 target) |
| Include live flight/hotel pricing in v1 | Budget realism is central to trust in recommendations | In progress (v1.1 target) |
| Launch with worldwide destination support | Prevents artificial scope boundaries that hurt discovery use cases | In progress (v1.1 target) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-26 after v1.0 milestone completion*
