# Search Clarification Contract

## Scope

This contract defines additions to the existing `POST /api/v1/search` conversational payload/response to support destination suggestions, preference capture, and comparison-ready recommendations.

## Request Contract (additive)

### `constraint_updates` additions

- `destination_candidates: string[]` — selected destinations for comparison mode.
- `date_flexibility: "fixed" | "few-days" | "week-flex" | "fully-flexible"`
- `flight_preferences: { nonstop?: boolean, max_travel_hours?: number }`
- `trip_style_tags: string[]` — e.g., `family-friendly`, `romantic`, `adventure`.
- `destination_selection_mode: "single" | "compare"`

### `clarification_answer` compatibility

- Existing `slot` + `answer_text` remains supported.
- New destination-step answers may reference suggestion IDs, labels, or explicit “don’t care”.

## Response Contract (additive)

### `clarification_state` additions

- `destination_suggestions`: array of suggestion options
  - `id: string`
  - `kind: "region" | "destination"`
  - `label: string`
  - `parent_region?: string`
  - `signals?: string[]`
  - `source: "curated" | "trend" | "extracted"`
- `supports_multi_destination_compare: boolean`
- `resolved_destination_candidates: string[]`

### `recommendation_packages` (new top-level field)

- Array of comparison-ready recommendation bundles:
  - `bundle_id: string`
  - `destination: string`
  - `score: number`
  - `rationale: string[]`
  - `estimated_total_cost?: number`
  - `comparison: { travel_time_fit, budget_fit, style_fit, flexibility_fit }`

### `flight_options` (new top-level field)

- `primary`: live options currently valid for selected route/date.
- `nearby_date_alternatives`: list of date-shift options with price deltas.
- `partial_availability`: boolean
- `warnings`: string[]

### `lodging_options` (new top-level field)

- `hotels`: option[]
- `bed_and_breakfasts`: option[]
- `vacation_rentals`: option[]
- `partial_availability`: boolean
- `warnings`: string[]

## Behavioral Guarantees

1. If destination is unresolved, response MUST include destination suggestions.
2. If user selects “don’t care”, response MUST include curated popular destination picks.
3. If multiple destinations are selected, response MUST preserve them for comparison.
4. Flight-first ordering MUST be preserved when flight inventory is requested.
5. If any provider fails/timeouts, response MUST remain valid with partial availability flags and warnings.

## Compatibility Notes

- Existing consumers of `clarification_state`, `results`, and `warnings` remain valid.
- New fields are additive and optional for backward compatibility.
