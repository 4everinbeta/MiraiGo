# Feature Specification: MiraiGo Baseline Product — Travel Discovery MVP

**Feature Branch**: `001-baseline-product-spec`

**Created**: 2026-05-16

**Status**: Baseline (describes shipped functionality — v1.0 complete + v1.1 Phase 10 complete)

**Input**: Derived from codebase inspection, GSD REQUIREMENTS.md (v1.0 archived + v1.1 active),
ROADMAP.md, and schema/service analysis.

---

## User Scenarios & Testing

### User Story 1 — Natural Language Travel Search (Priority: P1)

A leisure traveler types a free-form description of their trip idea (e.g., "somewhere warm in March,
around $2000") into the search bar. The system extracts whatever intent is present from the text and
begins the discovery flow immediately without requiring structured form input first.

**Why this priority**: This is the product's core value. Every other story depends on the initial
query being accepted as natural language.

**Independent Test**: A user can type any free-form string, submit it, and receive either a
clarification question or travel results — never a validation error demanding structured input.

**Acceptance Scenarios**:

1. **Given** a user with no prior session, **When** they type "beach trip next summer" and submit,
   **Then** the system responds with either a destination/timeline/budget clarification question or
   travel results — not a form validation error.
2. **Given** a query with fully specified intent (destination, dates, budget), **When** submitted,
   **Then** the system skips clarification and returns ranked travel results directly.
3. **Given** an empty query, **When** submitted, **Then** the system shows an appropriate prompt
   asking the user to describe their trip.

---

### User Story 2 — Guided Clarification Loop (Priority: P1)

When the system cannot confidently resolve destination, travel timeline, trip length, or budget from
the user's query, it asks one focused follow-up question at a time. The user answers, the answer is
saved as part of the session, and the next unanswered critical question is asked until all required
context is resolved.

**Why this priority**: Most real queries are vague. The clarification loop is what converts vague
intent into actionable search parameters.

**Independent Test**: Start with a vague query ("I want to travel somewhere"). Verify exactly one
question is shown at a time (never two simultaneously). Answer all four critical slots in sequence.
Verify recommendations appear after all are resolved.

**Acceptance Scenarios**:

1. **Given** a query with no destination, **When** submitted, **Then** the first clarification
   question asks specifically about destination — not timeline or budget first.
2. **Given** a partially answered session (destination resolved, timeline missing), **When**
   re-submitted, **Then** the system asks only about timeline, not destination again.
3. **Given** a user who answers "I don't know" to budget, **When** they continue, **Then** the
   system marks budget as explicitly unknown and proceeds to results rather than looping indefinitely.
4. **Given** all four critical slots (destination, timeline, trip length, budget) are resolved,
   **When** the search runs, **Then** travel results are returned without another clarification
   question.

---

### User Story 3 — Clarification Recap and Edit (Priority: P2)

After the clarification loop completes, the user sees a summary of all resolved travel constraints
as editable chips (e.g., "Paris", "July", "10 days", "$3,000"). They can tap any chip to revise
that constraint, and the system updates results accordingly without restarting the full flow.

**Why this priority**: Users refine their travel plans; edit continuity prevents frustrating
restarts.

**Independent Test**: Complete the clarification loop, then click the "destination" chip and change
it. Verify only destination-related slots are re-asked (not timeline or budget), and that new
results reflect the revised destination.

**Acceptance Scenarios**:

1. **Given** a completed clarification session, **When** the recap is displayed, **Then** each
   resolved slot appears as a labeled chip showing its current value.
2. **Given** the user edits the destination chip, **When** submitted, **Then** timeline and budget
   slots linked to destination are re-evaluated but other unrelated slots remain resolved.
3. **Given** the user clicks "Continue to Recommendations" without any edits, **When** clicked,
   **Then** the current resolved constraints are used as-is and results appear.

---

### User Story 4 — Mixed Stay and Flight Results (Priority: P2)

The search returns both hotel/stay options and flight options in a single unified results view. The
user can filter by provider, price range, or amenity. Each result clearly shows its price, provider,
and a link to complete the booking on the provider's site.

**Why this priority**: Discovery requires seeing the full cost picture (flights + accommodation)
together. Splitting them into separate searches defeats the purpose.

**Independent Test**: Submit a complete search request with both `stay` and `flight` inventory types.
Verify the results list contains at least one stay result and one flight result (when providers are
configured), each with a price, provider label, and redirect URL.

**Acceptance Scenarios**:

1. **Given** a search with both stay and flight inventory requested, **When** results are returned,
   **Then** results from both inventory types appear in the same response.
2. **Given** results are displayed, **When** the user filters by provider name, **Then** only results
   from that provider remain visible.
3. **Given** results are displayed, **When** the user sets a maximum price filter, **Then** only
   results at or below that price are shown.
4. **Given** a result card is displayed, **When** the user clicks the deep-link, **Then** they are
   redirected to the provider's site to complete the booking.

---

### User Story 5 — Provider Availability and Graceful Degradation (Priority: P2)

The user can see which travel providers are available and which are unavailable (e.g., because an
API credential is not configured). If one provider is unavailable, the search still returns results
from the remaining available providers — it does not show an error page.

**Why this priority**: In real deployments, not all provider credentials may be active. Users must
always see something useful.

**Independent Test**: Start the app without `DUFFEL_ACCESS_TOKEN` set. Submit a flight search.
Verify Duffel appears as "unavailable" in the provider status list, but Amadeus results (if
configured) or stay results still appear.

**Acceptance Scenarios**:

1. **Given** a provider's API credential is not configured, **When** the user views the provider
   status panel, **Then** that provider is shown as "unavailable" with a clear label.
2. **Given** one flight provider is unavailable, **When** a flight search runs, **Then** results
   from the remaining configured providers are still returned.
3. **Given** all flight providers are unavailable, **When** a stay+flight search runs, **Then**
   stay results are still returned and the response includes a warning about missing flight results.

---

### User Story 6 — Live Flight Search via Duffel and Amadeus (Priority: P2)

When Duffel and/or Amadeus API credentials are configured, the user receives real-time flight offers
sourced from those providers, not mock data. Offers include price, carrier, stops, departure and
arrival times, and a redirect to the booking page.

**Why this priority**: Real airfare data is the differentiator between a demo and a usable product
(shipped in v1.1 Phase 10).

**Independent Test**: Configure `DUFFEL_ACCESS_TOKEN` and submit a flight search with a concrete
origin, destination, and date. Verify at least one flight result contains a real carrier code,
real price, and real departure time (not mock placeholder values).

**Acceptance Scenarios**:

1. **Given** `DUFFEL_ACCESS_TOKEN` is set, **When** a flight search runs, **Then** flight results
   are sourced from the Duffel live API and include carrier code, stops, departure/arrival times.
2. **Given** Amadeus credentials are configured, **When** a flight search runs, **Then** flight
   results from Amadeus are included alongside Duffel results in the same response.
3. **Given** a live flight search, **When** results are returned, **Then** each flight result
   includes a total price, currency code, origin airport code, and destination airport code.

---

### Edge Cases

- What happens when both flight providers time out simultaneously? → Results contain only stay
  results plus a warning; the API returns 200 (not 500).
- What happens when the user submits the same query twice quickly? → The cached result is returned
  within the TTL window; a second live provider call is not made.
- What happens when the user's query contains a budget lower than any available flight price? →
  Results are returned with a warning; no results are silently hidden without explanation.
- What happens when clarification slot confidence is exactly at the threshold (0.65)? → Slot is
  treated as resolved and the next critical slot is asked.

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept a free-form natural language string as the primary search input.
- **FR-002**: System MUST extract destination, timeline, trip length, and budget intent from the
  query without requiring structured form fields to be filled first.
- **FR-003**: System MUST ask exactly one clarification question at a time when critical slots are
  unresolved, following the fixed priority order: destination → timeline → trip length → budget.
- **FR-004**: System MUST treat a slot as resolved when extracted confidence meets or exceeds 0.65.
- **FR-005**: System MUST allow users to explicitly mark a slot as unknown ("I don't know") and
  proceed to results.
- **FR-006**: System MUST present a recap of all resolved constraints as editable chips after the
  clarification loop completes.
- **FR-007**: System MUST re-evaluate destination-linked slots (timeline, budget) when the user edits
  the destination chip, without resetting unrelated slots.
- **FR-008**: System MUST return both stay (hotel/accommodation) and flight results in a single
  unified search response when both inventory types are requested.
- **FR-009**: System MUST include provider availability status in every search response.
- **FR-010**: System MUST return results from available providers when one or more providers are
  unavailable — a partial result set MUST be returned rather than an error.
- **FR-011**: System MUST source live flight offers from the Duffel API when `DUFFEL_ACCESS_TOKEN`
  is configured.
- **FR-012**: System MUST source live flight offers from the Amadeus API when Amadeus credentials
  are configured.
- **FR-013**: System MUST cache search results for 15 minutes to avoid redundant provider calls
  for identical queries within that window.
- **FR-014**: System MUST record each search run and provider execution in persistent storage for
  telemetry.
- **FR-015**: System MUST enforce per-provider timeouts to prevent a slow provider from blocking
  the entire search response.
- **FR-016**: System MUST expose a provider status endpoint that returns real-time health and
  configuration state for all registered providers.
- **FR-017**: System MUST support filtering results by provider, maximum price, amenities (stays),
  and nonstop preference (flights).
- **FR-018**: System MUST support traveler counts (adults, children, infants) as search parameters.

### Key Entities

- **SearchRequest**: Natural language query + optional structured overrides (destination, origin,
  dates, traveler counts, filters, clarification answers, constraint updates).
- **SearchResponse**: search_id, resolved filters, provider status list, result list (stays +
  flights), warnings, and optional clarification state.
- **ClarificationState**: Per-slot resolution state for destination, timeline, trip_length, budget,
  and weather — each with confidence score, value label, and source (user/extracted/system).
- **ClarificationSlotState**: Individual slot with value_label, normalized_value, confidence,
  ambiguous flag, explicit_unknown flag, and source.
- **StaySearchResult**: Provider, title, description, total price, nightly price, check-in/out,
  location label, amenities, redirect URL.
- **FlightSearchResult**: Provider, origin/destination airport codes, departure/arrival times,
  carrier codes, stops, duration, total price, redirect URL.
- **ProviderStatus**: Provider name, configured flag, healthy flag, supported inventory types,
  optional reason for unavailability.
- **SearchRun** / **ProviderRun**: Persistent telemetry records for each search and each provider
  execution within it.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: A user with a fully specified query (destination + dates + budget) receives travel
  results in a single turn — no clarification questions are asked.
- **SC-002**: A user with a fully vague query reaches travel results within 4 clarification turns
  (one question per critical slot: destination, timeline, trip length, budget).
- **SC-003**: When one flight provider is unavailable, at least one set of results (from stays or
  the remaining flight provider) is returned in the same response — never an empty result set with
  a 500 error.
- **SC-004**: Identical search queries submitted within 15 minutes return cached results without
  triggering additional provider API calls.
- **SC-005**: Provider status is visible to the user in every search response — no hidden failures.
- **SC-006**: A user can edit any resolved constraint chip and receive updated results without
  restarting the clarification flow from the beginning.
- **SC-007**: Live flight results from Duffel or Amadeus include all fields required to evaluate
  the offer: price, currency, carrier, stops, departure time, and arrival time.

---

## Assumptions

- **Users have a modern web browser** — no native mobile app is in scope.
- **Hotel results use redirect links** — no live hotel inventory API is integrated in v1.x; Expedia
  results redirect to Expedia's booking page.
- **Booking/checkout is out of scope** — MiraiGo is a discovery and redirect product only; payment
  processing does not occur within the app.
- **Itinerary generation is out of scope** — day-by-day planning is deferred to a future version.
- **Amadeus is in test-environment mode** — Amadeus credentials point to Amadeus's sandbox API;
  live production Amadeus traffic is not yet enabled.
- **Single-currency display (USD)** — all prices are normalized to USD for v1.x comparison.
- **No user accounts or persistent history** — each session is ephemeral; personalization based on
  prior trips is a future capability.
- **Weather preference** is a parsed clarification slot but is not yet a hard filter on results —
  it informs NLP context only.
