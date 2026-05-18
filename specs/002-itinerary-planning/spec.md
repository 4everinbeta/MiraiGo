# Feature Specification: Itinerary Proposal with Estimated and Live Pricing

**Feature Branch**: `001-baseline-product-spec` (planned addition to active milestone)

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Take a prompt like 'Given a total budget of $6000-$7500 for flight,
stay, and car (if needed), what are the best travel options for a family of three this summer,
considering natural getaways in places like Vancouver Island, New England, or the Pacific Northwest?'
and turn it into proposed itineraries with estimated costs. Then give them the ability to choose one
and have it return real values."

---

## User Scenarios & Testing

### User Story 1 — Receive Proposed Itinerary Options (Priority: P1)

A family traveler enters a prompt describing their total budget, party size, travel season, and
destination ideas. The system responds with 2–4 proposed itinerary options. Each option includes a
suggested destination, estimated total cost (broken down by flight, accommodation, and car rental
if applicable), and a brief rationale for the recommendation. No real booking has happened yet —
these are informed estimates.

**Why this priority**: This is the primary new capability. All other stories depend on proposals
being generated first.

**Independent Test**: Submit the sample prompt. Verify the response contains at least two distinct
itinerary options, each with a destination name, estimated total cost within the stated budget range,
and a cost breakdown.

**Acceptance Scenarios**:

1. **Given** a prompt with a budget range, party size, travel season, and destination ideas, **When**
   submitted, **Then** the system returns 2–4 itinerary proposals without asking clarification
   questions (since all critical information is present).
2. **Given** a prompt missing the travel season, **When** submitted, **Then** the clarification loop
   asks for a timeline before generating proposals.
3. **Given** a prompt specifying "car if needed", **When** the destination requires ground transport,
   **Then** the car rental cost is included in the estimate; if the destination is walkable or
   transit-accessible, car rental is omitted.
4. **Given** two proposals are shown, **When** the estimates are displayed, **Then** both totals fall
   within the user's stated budget range or are flagged as "over budget" with a note explaining why
   they were still included.

---

### User Story 2 — Choose a Proposal and Retrieve Live Prices (Priority: P1)

After reviewing the estimated proposals, the user selects one itinerary. The system then goes out
to live travel providers and fetches real flight offers, real accommodation options, and (if
applicable) real car rental options for that specific itinerary. The user sees updated real prices,
not estimates.

**Why this priority**: The value of the selection flow is converting a rough plan into actionable
real-world offers the user can book.

**Independent Test**: Generate proposals, select one, and trigger live pricing. Verify the response
contains at least one live flight result (with carrier and real departure/arrival) and at least one
accommodation result for the selected destination and dates.

**Acceptance Scenarios**:

1. **Given** a proposal is selected, **When** the user confirms, **Then** the system fetches live
   flight offers for the proposal's origin–destination pair and dates.
2. **Given** live pricing completes, **When** results are displayed, **Then** the user sees real
   prices from available providers alongside a "Book" or redirect link for each offer.
3. **Given** a live flight provider is unavailable during pricing, **When** the result loads,
   **Then** available providers still return results and the unavailable provider is labeled
   "currently unavailable" — no error page is shown.
4. **Given** live prices come back higher than the estimate, **When** displayed, **Then** the
   real price is shown clearly; the user is not misled by the original estimate.

---

### User Story 3 — Partially Specified Prompt Triggers Clarification (Priority: P2)

When the user's itinerary prompt is missing one or more critical pieces (budget, party size, travel
window), the system asks one clarification question at a time — consistent with the existing
clarification loop — before generating proposals.

**Why this priority**: Users will frequently omit details. The existing clarification UX must extend
naturally to cover itinerary-specific slots.

**Independent Test**: Submit a prompt with destination ideas but no budget or party size. Verify
the system asks for party size (if missing) or budget (if missing) before generating any proposals.

**Acceptance Scenarios**:

1. **Given** a prompt with no budget mentioned, **When** submitted, **Then** the clarification
   loop asks the user for their budget before generating proposals.
2. **Given** a prompt with no party size, **When** submitted, **Then** the system asks how many
   travelers are in the group before generating proposals.
3. **Given** all critical slots are answered through clarification, **When** the loop completes,
   **Then** the proposal generation runs automatically without requiring the user to re-submit.

---

### User Story 4 — Cost Breakdown is Visible and Understandable (Priority: P2)

Each itinerary proposal shows a clear cost breakdown separating estimated flight cost, estimated
accommodation cost, and estimated car rental cost (if applicable). The breakdown helps users
understand where the budget is going before they commit to live pricing.

**Why this priority**: Users evaluating $6,000–$7,500 trips need to understand the composition of
the estimate, not just the total.

**Independent Test**: Inspect a proposal response. Verify each proposal object contains at least
three fields: total estimated cost, flight cost estimate, and accommodation cost estimate. If car
is included, a car cost estimate must also be present.

**Acceptance Scenarios**:

1. **Given** an itinerary proposal is generated, **When** the user views it, **Then** the total
   estimate is visibly broken down into flight, stay, and car (if applicable) components.
2. **Given** a proposal includes car rental, **When** car is not needed for a different proposal,
   **Then** that proposal's breakdown explicitly shows car cost as "not needed" or omits it — the
   user is not left wondering.
3. **Given** costs are estimates, **When** displayed, **Then** each estimate is clearly labeled as
   approximate (e.g., "~$1,800") rather than precise figures.

---

### Edge Cases

- What if the user's budget is below any realistic option for their stated destinations? → Return
  the cheapest available proposals with a clear note that they exceed the stated budget.
- What if no live flight offers exist for the selected proposal's dates? → Show accommodation
  results only and surface a warning that flight pricing was unavailable.
- What if the user selects a proposal and immediately changes a parameter (party size)? → Trigger
  a new live pricing fetch with the updated parameters; do not show stale results.
- What if two proposals produce the same destination? → Proposals MUST differ on at least one
  meaningful dimension (e.g., duration, accommodation type, or routing).

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a natural language prompt containing budget range, party size,
  travel season, and destination preferences as the input to proposal generation.
- **FR-002**: System MUST return 2–4 distinct itinerary proposals in a single response when all
  critical inputs are present.
- **FR-003**: Each itinerary proposal MUST include: destination name, estimated total cost,
  estimated flight cost, estimated accommodation cost, and estimated car rental cost (if applicable).
- **FR-004**: Estimated costs MUST be labeled as approximate and fall within the user's stated
  budget range, or be flagged as over-budget with an explanatory note.
- **FR-005**: System MUST reuse the existing clarification loop to ask for missing critical inputs
  (budget, party size, travel window) before generating proposals.
- **FR-006**: System MUST expose a separate "price selected itinerary" action that fetches live
  offers from configured flight and stay providers for the chosen proposal.
- **FR-007**: Live pricing MUST include real flight offers (carrier, stops, departure/arrival) and
  real or redirect-based accommodation offers for the selected destination and dates.
- **FR-008**: Live pricing MUST follow the existing graceful degradation pattern — partial results
  from available providers MUST be returned when one provider is unavailable.
- **FR-009**: Car rental MUST be included in estimates and live pricing when the destination and
  trip type indicate ground transport is needed; it MUST be omitted when not needed.
- **FR-010**: System MUST distinguish clearly between estimated costs (proposals) and live prices
  (post-selection) in both the API response and the UI.

### Key Entities

- **ItineraryProposal**: A generated itinerary option — destination, duration, travel window,
  party size, cost estimate breakdown (flight, stay, car), rationale summary, needs-car flag.
- **ItineraryCostEstimate**: Total, flight component, stay component, optional car component —
  all labeled as estimates with currency code.
- **ItinerarySelection**: The user's chosen proposal — references proposal ID and may carry
  constraint overrides (adjusted dates, party size changes).
- **LivePricingResult**: The real-price counterpart of a proposal — flight results, stay results,
  car redirect (if applicable), fetched from live providers for specific dates and traveler counts.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: A user submitting a fully specified prompt (budget + party size + season +
  destinations) receives 2–4 itinerary proposals without any clarification questions.
- **SC-002**: Every proposal's estimated total cost either falls within the user's stated budget
  range or is explicitly flagged as over budget.
- **SC-003**: After the user selects a proposal, live pricing results are returned within 15
  seconds under normal provider response conditions.
- **SC-004**: Live pricing returns results from at least one provider even when one flight provider
  is unavailable — no full-failure empty response.
- **SC-005**: The cost breakdown in each proposal clearly separates flight, stay, and car
  components so users can evaluate trade-offs without ambiguity.

---

## Assumptions

- **Origin airport is known or inferable** — the user's origin is either stated in the prompt or
  already resolved in the clarification session (e.g., from a prior search turn).
- **Car rental uses a redirect model for v1** — no live car rental inventory API is integrated;
  car estimates are based on market-rate bands and the car result links to a search on a redirect
  partner (consistent with the hotel model).
- **Estimates use cost bands, not live pre-fetch** — flight and stay estimates are derived from
  historical cost-band data per destination and season, not from live API calls at proposal time.
  Live pricing only happens after the user selects a proposal.
- **2026 summer = June–August** — unless the user specifies a different season or date range.
- **"Family of three" → adults: 2, children: 1** unless the user specifies ages or a different
  composition.
- **Proposals are not saved across sessions** — the proposal set is ephemeral and tied to the
  current session; no persistence of proposals between page refreshes.
