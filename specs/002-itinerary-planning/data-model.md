# Data Model: Itinerary Proposal with Estimated and Live Pricing

**Feature**: Itinerary Proposal
**Date**: 2026-05-16

---

## Core Entities

### ItineraryProposal

Represents one generated itinerary option before the user selects it.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `proposal_id` | str | uuid, required | Client-held; echoed back in price request |
| `destination` | str | required, max 120 | e.g., "Vancouver Island, BC" |
| `destination_region_key` | str | required | Key into cost_bands lookup (e.g., "vancouver-island") |
| `travel_window` | SearchDateRange | required | Resolved dates or season-anchored range |
| `duration_nights` | int | ≥ 1, ≤ 30 | Estimated trip length |
| `travelers` | TravelerCounts | required | Adults, children, infants |
| `needs_car` | bool | required | Determined by destination classification |
| `cost_estimate` | ItineraryCostEstimate | required | Breakdown by component |
| `rationale` | str | max 280 | Why this destination was suggested |
| `within_budget` | bool | required | True if total estimate ≤ budget_max |
| `over_budget_note` | str \| None | max 160 | Explanation if within_budget is False |

---

### ItineraryCostEstimate

Approximate cost breakdown — clearly labeled as estimates, not live prices.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `total_estimated` | float | ≥ 0 | Sum of all components |
| `flight_estimated` | float | ≥ 0 | Round-trip for all travelers |
| `stay_estimated` | float | ≥ 0 | Total for all nights |
| `car_estimated` | float \| None | ≥ 0 | Omitted if needs_car is False |
| `currency_code` | str | 3 chars, default "USD" | |
| `confidence` | Literal["low", "medium", "high"] | required | Band width relative to budget |

---

### ItineraryProposeRequest

The input to the proposal endpoint — mirrors SearchRequest pattern.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `query` | str \| None | max 2000 | Free-text prompt; required unless clarification_answer set |
| `travelers` | TravelerCounts | default adults=2 children=1 | Can be extracted from query |
| `budget_range` | ClarificationBudgetRange \| None | | Extracted or provided |
| `candidate_destinations` | List[str] \| None | | Extracted or provided |
| `travel_window` | SearchDateRange \| None | | Extracted or provided |
| `include_car` | bool \| None | | None = auto; True/False = override |
| `clarification_answer` | ClarificationAnswer \| None | | For multi-turn loop |
| `currency_code` | str | 3 chars, default "USD" | |

---

### ItineraryProposeResponse

| Field | Type | Notes |
|---|---|---|
| `session_id` | str | uuid |
| `proposals` | List[ItineraryProposal] | 0–4 items; 0 if clarification needed |
| `clarification_state` | ClarificationState \| None | Present if critical slots missing |
| `applied_inputs` | dict | Echo of resolved budget, travelers, window |
| `warnings` | List[str] | |

---

### ItineraryPriceRequest

Sent by the frontend after the user selects a proposal.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `proposal_id` | str | required | Echoed from ItineraryProposal |
| `proposal_snapshot` | ItineraryProposal | required | Full proposal (client-held state) |
| `travelers` | TravelerCounts | required | May differ from proposal if user adjusted |
| `currency_code` | str | default "USD" | |

---

### ItineraryPriceResponse

| Field | Type | Notes |
|---|---|---|
| `search_id` | str | uuid; links to SearchRun telemetry |
| `proposal_id` | str | echoed |
| `flight_results` | List[FlightSearchResult] | Live results; reuses existing schema |
| `stay_results` | List[StaySearchResult] | Live results; reuses existing schema |
| `car_redirect_url` | str \| None | Redirect to car search if needs_car |
| `car_redirect_label` | str \| None | e.g., "Search car rentals on Expedia" |
| `provider_status` | List[ProviderStatus] | Reuses existing schema |
| `warnings` | List[str] | |

---

## Cost Band Lookup (src/app/data/cost_bands.py)

```python
# Structure: {region_key: {season: {component: (low_usd, high_usd)}}}
# Per-traveler for flights; per-night for stays; per-day for car

COST_BANDS = {
    "vancouver-island": {
        "summer": {
            "flight_per_pax": (300, 700),
            "stay_per_night": (150, 400),
            "car_per_day": (60, 120),
            "car_needed": True,
        }
    },
    "new-england": {
        "summer": {
            "flight_per_pax": (150, 450),
            "stay_per_night": (120, 350),
            "car_per_day": (50, 100),
            "car_needed": True,
        }
    },
    "pacific-northwest": {
        "summer": {
            "flight_per_pax": (200, 500),
            "stay_per_night": (130, 350),
            "car_per_day": (55, 110),
            "car_needed": True,
        }
    },
}
```

---

## State Transitions

```
User submits prompt
        ↓
[All critical slots present?]
  No → ClarificationState returned (existing loop)
  Yes ↓
Proposal generation
        ↓
ItineraryProposeResponse (proposals: 2–4)
        ↓
User selects one proposal
        ↓
POST /itinerary/price
        ↓
Live provider fan-out (Duffel + Amadeus flights, Expedia redirect stay)
        ↓
ItineraryPriceResponse (real prices + redirect links)
```

---

## Schema Reuse

The following existing schemas are reused without modification:

| Existing Schema | Used in |
|---|---|
| `TravelerCounts` | ItineraryProposeRequest, ItineraryProposal |
| `ClarificationBudgetRange` | ItineraryProposeRequest |
| `ClarificationAnswer` | ItineraryProposeRequest (multi-turn) |
| `ClarificationState` | ItineraryProposeResponse |
| `SearchDateRange` | ItineraryProposal |
| `FlightSearchResult` | ItineraryPriceResponse |
| `StaySearchResult` | ItineraryPriceResponse |
| `ProviderStatus` | ItineraryPriceResponse |
