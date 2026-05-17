# Data Model — Destination Guided Recommendations

## 1. ClarificationSessionState

Represents turn-by-turn clarification progress for a search intent.

### Fields

- `search_id` (string, required): Unique session identifier.
- `query` (string, required): Original natural-language user intent.
- `slot_states` (object, required): Current state for critical slots (`destination`, `timeline`, `trip_length`, `budget`) and optional slots (`weather`, flexibility/preference slots).
- `next_question` (object, optional): Next prompt to ask.
- `history` (array, required): Ordered answer/edit/unknown events.
- `all_critical_slots_resolved` (boolean, required): Gate for recommendation generation.

### Validation rules

- Must maintain one active `next_question` at a time when unresolved slots remain.
- `history` entries must reference valid slots.
- Slot confidence values must be in `[0,1]`.

## 2. DestinationSuggestion

Represents a destination-narrowing option shown during clarification.

### Fields

- `id` (string, required): Stable option identifier.
- `kind` (enum, required): `region` | `destination`.
- `label` (string, required): User-facing display text.
- `parent_region` (string, optional): Region grouping when kind is destination.
- `signals` (array[string], optional): Matching reasons (e.g., warm, beach, family-friendly).
- `popularity_score` (number, optional): Relative ranking value.
- `source` (enum, required): `curated` | `trend` | `extracted`.

### Validation rules

- At least one `DestinationSuggestion` must be available when destination is unresolved.
- `kind=destination` options should include a geography label or parent context.

## 3. PreferenceProfile

Resolved traveler constraints used for recommendation packaging.

### Fields

- `destination_candidates` (array[string], required): One or more chosen destinations.
- `trip_length_days` (integer, optional): Intended stay length.
- `budget_range` (object, optional): Min/max and currency.
- `date_flexibility` (enum, optional): `fixed` | `few-days` | `week-flex` | `fully-flexible`.
- `flight_preferences` (object, optional): Non-stop preference, max preferred travel duration.
- `trip_style_tags` (array[string], optional): Family-friendly, romantic, etc.

### Validation rules

- Recommendation generation requires at least one destination candidate.
- `budget_range.minimum <= budget_range.maximum` when both present.
- Duration fields must be positive.

## 4. RecommendationBundle

Candidate recommendation ready for display and comparison.

### Fields

- `bundle_id` (string, required)
- `destination` (string, required)
- `score` (number, required)
- `rationale` (array[string], required): Human-readable why-this-option statements.
- `estimated_total_cost` (number, optional)
- `confidence` (number, optional)
- `comparable_dimensions` (object, required): Cost, travel time, style fit, flexibility fit.

### Validation rules

- Must include at least one rationale item.
- Comparable dimensions must exist for any option shown in comparison mode.

## 5. FlightOptionGroup

Live flight options plus date-adjacent alternatives.

### Fields

- `primary_options` (array, required)
- `date_alternatives` (array, optional): Nearby date options with pricing deltas.
- `origin` (string, required for flight shopping)
- `destination` (string, required)
- `travel_window` (object, required)
- `partial_availability` (boolean, required)
- `warnings` (array[string], optional)

### Validation rules

- Flight shopping requires `origin`, `destination`, and travel window.
- If providers partially fail, `partial_availability=true` and warnings must be populated.

## 6. LodgingOptionGroup

Stay inventory aligned to selected flight/date context.

### Fields

- `destination` (string, required)
- `check_in` (date, required)
- `check_out` (date, required)
- `categories` (object, required): Grouped sets for hotels, B&Bs, vacation rentals.
- `partial_availability` (boolean, required)
- `warnings` (array[string], optional)

### Validation rules

- Lodging dates must be consistent with selected trip window.
- Category keys may be empty but must be present when lodging response is returned.

## Relationships

- `ClarificationSessionState` produces a `PreferenceProfile`.
- `PreferenceProfile` feeds `RecommendationBundle` generation.
- Selected bundle context drives `FlightOptionGroup`.
- Chosen flight/date context drives `LodgingOptionGroup`.
