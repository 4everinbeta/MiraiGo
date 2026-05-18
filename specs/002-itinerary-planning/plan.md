# Implementation Plan: Itinerary Proposal with Estimated and Live Pricing

**Branch**: `002-itinerary-planning` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-itinerary-planning/spec.md`

---

## Summary

Extend MiraiGo's existing search pipeline to generate 2–4 estimated itinerary proposals from a
natural language prompt, then — after the user selects one — retrieve real prices from live
providers. The feature builds directly on top of the current provider adapter registry, clarification
loop, and NLP intent extraction rather than replacing them.

---

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5 / Next.js 16.1.6 (frontend)

**Primary Dependencies**: FastAPI, SQLAlchemy, Amadeus provider, Duffel provider, Expedia redirect,
existing NLP (`extract_intent`), existing clarification service

**Storage**: PostgreSQL (search/provider run telemetry — existing), Redis (response cache — existing)

**Testing**: pytest + pytest-cov (backend), Jest + Testing Library (frontend unit),
Playwright + axe-core (E2E)

**Target Platform**: Docker Compose locally; Railway/Azure split-service in production

**Project Type**: Full-stack web service (FastAPI API + Next.js frontend)

**Performance Goals**: Proposal generation < 500ms (no live API calls); live pricing < 15s
(matches existing PROVIDER_TIMEOUT_SECONDS = 12.0 ceiling)

**Constraints**: Car rental = redirect-only in v1 (no live inventory API); cost estimates use
pre-configured cost bands (no live pre-fetch at proposal time); proposals are ephemeral (session
only, no DB persistence needed beyond existing SearchRun telemetry)

**Scale/Scope**: Same scale as current search (~concurrent users as existing deployment)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Notes |
|-----------|-------|-------|
| I. Natural Language-First | ✅ PASS | Prompt-driven input; proposals flow from free-text query, not a structured form |
| II. Full-Stack Separation + Layering | ✅ PASS | New route (`/api/v1/itinerary`) → new service (`itinerary_service`) → existing providers; no logic inlined into route |
| III. Test Coverage Non-Negotiable | ✅ PASS | pytest tests required for all new service and NLP code; Jest tests for new frontend components; Playwright E2E for the proposal→select→price flow |
| IV. Security & Config Hygiene | ✅ PASS | No new secrets required; car redirect uses same pattern as Expedia hotel redirect |
| V. Simplicity & Focused Modules | ✅ PASS | Itinerary service is a focused orchestrator; cost-band estimation is a stateless helper; no new layers beyond routes→services→providers |
| VI. Resilience & Graceful Degradation | ✅ PASS | Live pricing step follows existing graceful degradation; missing providers return partial results |

No violations. No complexity exceptions required.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-itinerary-planning/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── itinerary-propose.md   # POST /api/v1/itinerary/propose
│   └── itinerary-price.md     # POST /api/v1/itinerary/price
```

### Source Code

```text
src/app/
├── api/v1/
│   └── itinerary.py             # New: propose + price route handlers
├── services/
│   └── itinerary.py             # New: proposal generation + live pricing orchestration
├── nlp/
│   └── intent.py                # Extend: parse party size, budget range, destination list
├── schemas/
│   └── itinerary.py             # New: ItineraryProposal, ItineraryCostEstimate,
│                                #       ItinerarySelection, LivePricingResponse
├── data/
│   └── cost_bands.py            # New: per-destination seasonal cost band lookup table
└── providers/
    └── (existing — no changes needed for v1)

web/src/
├── components/
│   └── itinerary/
│       ├── ItineraryProposalList.tsx   # New: shows 2-4 proposal cards
│       ├── ItineraryProposalCard.tsx   # New: single proposal with cost breakdown
│       └── ItineraryPricingResult.tsx  # New: live pricing results post-selection
├── lib/
│   └── api.ts                          # Extend: add itinerary propose + price API calls
└── app/
    └── page.tsx                        # Extend: add itinerary flow state alongside search state

src/tests/
├── services/
│   └── test_itinerary.py        # New
├── nlp/
│   └── test_intent.py           # Extend: cover party size + budget range + destination list
└── api/
    └── test_itinerary.py        # New

web/src/components/itinerary/__tests__/
├── ItineraryProposalList.test.tsx
└── ItineraryProposalCard.test.tsx

web/tests/e2e/
└── itinerary.test.ts            # New: full proposal → select → live price Playwright flow
```

---

## Phase 0: Research

### 0-A: Cost Band Strategy

**Decision**: Use a static, version-controlled cost band table (`src/app/data/cost_bands.py`).
Each entry maps `(destination_region, season, inventory_type)` → `(low_usd, high_usd)` per
traveler per unit (per night for stay, total for flight).

**Rationale**: Live pre-fetching at proposal time would add 12s+ of latency for each proposal
option before the user has even selected one. A cost band table delivers sub-500ms proposals
while being transparent and easily updated. After selection, live pricing replaces the estimates.

**Alternatives considered**:
- *Amadeus Price Insights API*: Would give real historical fare data but adds API dependency,
  credentials, and latency at proposal time. Deferred to v2.
- *LLM-generated estimates*: Non-deterministic, hard to test, adds new dependency. Rejected.

**Initial seed destinations** (to cover the example prompt):
| Region | Flight band/pax (US origin) | Stay band/night | Car band/day |
|---|---|---|---|
| Vancouver Island | $300–$700 | $150–$400 | $60–$120 |
| New England | $150–$450 | $120–$350 | $50–$100 |
| Pacific Northwest | $200–$500 | $130–$350 | $55–$110 |
| (expandable — any destination extractable by NLP) | | | |

---

### 0-B: NLP Extensions for Itinerary Prompts

**Decision**: Extend `extract_intent()` with three new extraction targets:

1. **Party composition**: parse "family of three", "couple", "solo", "two adults one child" →
   populate `TravelerCounts`.
2. **Budget range**: already partially handled; extend to capture `$X–$Y` range syntax and map to
   `ClarificationBudgetRange(minimum=X, maximum=Y)`.
3. **Destination list**: extract multiple candidate destinations ("Vancouver Island, New England,
   or the Pacific Northwest") → `List[str]` of candidate regions.

**Rationale**: All three are present in the example prompt. The existing `extract_intent` already
handles single destinations and qualitative budgets; we extend rather than replace.

---

### 0-C: Car Rental Inclusion Logic

**Decision**: Determine "car needed" based on a simple rule per destination region:
- If the destination is classified as `urban` (transit-accessible city) → car not needed.
- If the destination is classified as `regional` (island, national park, rural area) → car needed.
- Classification lives in `cost_bands.py` alongside the cost data.

**Rationale**: This avoids asking the user an extra clarification question in the common case.
The "if needed" language in the original prompt aligns with this automatic determination.

---

### 0-D: Proposal Generation Algorithm

**Decision**: For each candidate destination extracted from the prompt:
1. Resolve travel window → default to "July" (peak summer) if season given but no exact dates.
2. Look up cost bands for (destination, season, flight + stay + car-if-needed).
3. Scale flight + car by traveler count; scale stay by (nights × nightly_band × room_estimate).
4. Sum → compare to user's budget range.
5. Rank by: (a) within budget? (b) best fit score from existing `rank_results` logic.
6. Return top 2–4 proposals; include over-budget ones if fewer than 2 in-budget options exist.

---

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` (generated below).

---

### API Contracts

#### `POST /api/v1/itinerary/propose`

```
Input:  ItineraryProposeRequest
Output: ItineraryProposeResponse
```

**Request fields**:
- `query` (str): Free-text prompt (required unless clarification_answer provided)
- `travelers` (TravelerCounts): defaults to adults=2, children=1 if not specified
- `budget_range` (ClarificationBudgetRange | None): e.g., {minimum: 6000, maximum: 7500}
- `candidate_destinations` (List[str] | None): extracted or user-provided
- `travel_window` (SearchDateRange | None): extracted season/dates
- `include_car` (bool | None): None = auto-determine per destination
- `clarification_answer` (ClarificationAnswer | None): for multi-turn clarification flow
- `currency_code` (str): default "USD"

**Response fields**:
- `session_id` (str): links to clarification state if loop is active
- `proposals` (List[ItineraryProposal]): 0–4 proposals (0 if clarification needed)
- `clarification_state` (ClarificationState | None): set if critical slots are missing
- `warnings` (List[str])

---

#### `POST /api/v1/itinerary/price`

```
Input:  ItineraryPriceRequest
Output: ItineraryPriceResponse
```

**Request fields**:
- `proposal_id` (str): ID of the selected ItineraryProposal
- `proposal_snapshot` (ItineraryProposal): full proposal data (client-held, no server state)
- `travelers` (TravelerCounts)
- `currency_code` (str): default "USD"

**Response fields**:
- `search_id` (str)
- `proposal_id` (str)
- `flight_results` (List[FlightSearchResult]): live results from Duffel/Amadeus
- `stay_results` (List[StaySearchResult]): live results from Expedia redirect
- `car_redirect_url` (str | None): car rental redirect if proposal includes car
- `provider_status` (List[ProviderStatus])
- `warnings` (List[str])

---

### quickstart.md excerpt

```bash
# Test proposal generation locally
curl -X POST http://localhost:8000/api/v1/itinerary/propose \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Given a total budget of $6000-$7500 for flight, stay, and car (if needed), what are the best travel options for a family of three this summer, considering natural getaways in places like Vancouver Island, New England, or the Pacific Northwest?"
  }'

# Then price the first returned proposal (use proposal_id from above)
curl -X POST http://localhost:8000/api/v1/itinerary/price \
  -H "Content-Type: application/json" \
  -d '{
    "proposal_id": "<id-from-above>",
    "proposal_snapshot": { ... },
    "travelers": {"adults": 2, "children": 1, "infants": 0},
    "currency_code": "USD"
  }'
```

---

## Complexity Tracking

No constitution violations to justify. Architecture follows the established routes → services →
providers pattern without additional layers.

---

## Post-Phase 1 Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Natural Language-First | ✅ PASS | `POST /itinerary/propose` accepts free text; no structured form required |
| II. Full-Stack Separation + Layering | ✅ PASS | Route → ItineraryService → existing providers; schemas in `schemas/itinerary.py` |
| III. Test Coverage | ✅ PASS | Test files scoped per domain; E2E covers full flow |
| IV. Security | ✅ PASS | No new secrets; car redirect uses same redirect-link pattern |
| V. Simplicity | ✅ PASS | `cost_bands.py` is a plain dict lookup; `itinerary_service` is a focused orchestrator |
| VI. Resilience | ✅ PASS | `/price` endpoint returns partial results if a provider is down |
