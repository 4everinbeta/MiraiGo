# MiraiGo Travel Discovery

## Current State

- **Shipped milestone:** v1.0 (2026-04-26)
- **Delivered:** End-to-end natural-language intent clarification with deterministic follow-up turns and continuity across answer/edit/continue flows.
- **Verification posture:** INTENT-01..04 closed with automated + human evidence; milestone audit closed as `tech_debt` (non-blocking items only).

## Current Milestone: v1.1 Realtime Airfare Integrations

**Goal:** Add reliable realtime airfare pricing through Amadeus and Duffel so search results surface current flight cost context.

**Target features:**
- Amadeus flight pricing adapter integrated into search flow
- Duffel flight pricing adapter integrated into search flow
- Unified airfare normalization and provenance metadata for result comparison

## Next Milestone Goals

- Deliver flight-only realtime airfare integrations for two providers (Amadeus + Duffel).
- Add normalization/freshness handling for cross-provider airfare comparison.
- Keep hotels and checkout flows out of scope for this milestone.

## What This Is

MiraiGo Travel Discovery is a travel planning website for leisure travelers that turns loose natural-language prompts into ranked destination suggestions. Users can describe broad preferences, and MiraiGo asks targeted follow-up questions when details are missing. The result is a guided, conversational way to narrow travel options by geography, weather, budget, and timeline.

## Core Value

Given vague travel intent, MiraiGo reliably converts it into personalized, ranked destination suggestions with clear rationale.

## Requirements

### Validated

- INTENT-01..04 validated and shipped in milestone v1.0.

### Active

- [ ] User can receive realtime airfare context sourced from Amadeus and Duffel during discovery.
- [ ] Airfare results include consistent normalized fields and provider freshness/provenance metadata.
- [ ] Destination ranking can consume realtime airfare context without breaking clarification flow continuity.

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
*Last updated: 2026-04-26 after v1.1 milestone kickoff*
