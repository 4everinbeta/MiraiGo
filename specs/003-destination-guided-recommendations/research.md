# Phase 0 Research — Destination Guided Recommendations

## Decision 1: Destination-first clarification remains the first unresolved critical slot

- **Decision**: Keep destination as the first critical clarification slot and add suggestion payloads when destination is missing or ambiguous.
- **Rationale**: Destination drives feasibility for timeline, budget realism, and provider availability; capturing it first reduces downstream rework.
- **Alternatives considered**:
  - Ask budget first: rejected because budget depends heavily on destination market.
  - Ask timeline first: rejected because seasonal guidance still needs destination context.

## Decision 2: Suggestion model supports both regions and destinations

- **Decision**: Represent suggestions as a unified option list with `kind` (`region` or `destination`) and allow multi-select.
- **Rationale**: Users can narrow from broad geography to concrete choices without switching interaction modes.
- **Alternatives considered**:
  - Regions-only step: rejected because it adds one extra round trip before actionable comparisons.
  - Destination-only list: rejected because it overwhelms users who are still broad in intent.

## Decision 3: “Don’t care” fallback uses curated trend-backed popular picks

- **Decision**: When user indicates no location preference, return a curated set of popular beach destinations ranked by trip-style match (warm/beach/family/romantic) with transparent “why suggested” text.
- **Rationale**: Maintains conversational momentum and aligns with product goal of proactive inspiration.
- **Alternatives considered**:
  - Random destinations: rejected due to low relevance.
  - Require user to type a location anyway: rejected as high-friction.

## Decision 4: Extend existing `/api/v1/search` contract rather than adding new endpoint

- **Decision**: Continue using `/api/v1/search` and expand `clarification_state` with suggestion structures and flexibility/preference slots.
- **Rationale**: Preserves client compatibility and existing orchestration path in `search_service`.
- **Alternatives considered**:
  - New `/clarify` endpoint: rejected due to duplicated session/state handling.
  - Frontend-only suggestion generation: rejected because it bypasses backend ranking logic.

## Decision 5: Multi-destination comparison is first-class in recommendation output

- **Decision**: Persist user-selected candidate destinations and produce comparison-ready recommendation bundles before live shopping finalization.
- **Rationale**: Directly supports requested “select from or compare a few” behavior.
- **Alternatives considered**:
  - Single-destination only: rejected because it blocks comparison use case.
  - Separate comparison mode toggle: rejected for unnecessary UX complexity.

## Decision 6: Flight-first live pricing with nearby-date alternatives and graceful partial responses

- **Decision**: Keep flight-first ordering and include date-adjacent alternatives as an additional option group; continue returning partial results when providers timeout/fail.
- **Rationale**: Matches user expectation (Google Flights-like date alternatives) while honoring constitution resilience rules.
- **Alternatives considered**:
  - Lodging-first: rejected when air travel materially affects total trip cost.
  - Fail whole request on provider outage: rejected due to poor user experience.

## Decision 7: Lodging follow-through bound to selected flight/date context

- **Decision**: After flight/date selection, request lodging options scoped to chosen destination and travel window and grouped by lodging category.
- **Rationale**: Produces coherent itinerary decisions and avoids mismatched flight/lodging timelines.
- **Alternatives considered**:
  - Unscoped lodging list: rejected due to weak relevance.
  - Force booking before lodging browse: rejected as overly restrictive for discovery flow.

## Decision 8: Benchmark parity-plus against leading AI travel assistants

- **Decision**: Use Layla.ai-style conversational guidance as benchmark context, with explicit differentiation in transparency and side-by-side comparison depth.
- **Rationale**: Product direction calls for parity in guidance quality and superiority in recommendation explainability.
- **Alternatives considered**:
  - Ignore competitive baseline: rejected because success criteria include comparative preference outcomes.
  - Copy interaction patterns verbatim: rejected in favor of differentiated UX/value.
