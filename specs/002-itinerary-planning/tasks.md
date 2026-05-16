---

description: "Task list for Itinerary Proposal with Estimated and Live Pricing"
---

# Tasks: Itinerary Proposal with Estimated and Live Pricing

**Input**: Design documents from `specs/002-itinerary-planning/`

**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅

**Tests**: Included — required by Constitution Principle III (Test Coverage is Non-Negotiable).

**Organization**: Tasks are grouped by user story. US1 and US2 are both P1 and can be worked in
parallel once Phase 2 (Foundational) completes. US3 and US4 are P2 and can follow independently.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4)

---

## Phase 1: Setup

**Purpose**: Create new directories and empty init files so Python/TS modules resolve correctly.

- [ ] T001 Create `src/app/data/__init__.py` (empty module init for new data package)
- [ ] T002 [P] Create `web/src/components/itinerary/.gitkeep` placeholder so directory exists before component files are added

**Checkpoint**: Directory scaffolding ready — foundational files can now be created.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schemas, cost band data, NLP extensions, and the service skeleton must all exist before
any user story work can begin. No user story depends on another user story, but all depend on this
phase.

**⚠️ CRITICAL**: All four tasks below block every user story. Complete this phase before Phase 3.

- [ ] T003 Create `src/app/schemas/itinerary.py` — define all Pydantic models: `ItineraryCostEstimate` (total_estimated, flight_estimated, stay_estimated, car_estimated, currency_code, confidence: Literal["low","medium","high"]), `ItineraryProposal` (proposal_id, destination, destination_region_key, travel_window: SearchDateRange, duration_nights, travelers: TravelerCounts, needs_car, cost_estimate: ItineraryCostEstimate, rationale, within_budget, over_budget_note), `ItineraryProposeRequest` (query, travelers, budget_range, candidate_destinations, travel_window, include_car, clarification_answer, currency_code), `ItineraryProposeResponse` (session_id, proposals, clarification_state, applied_inputs, warnings), `ItineraryPriceRequest` (proposal_id, proposal_snapshot, travelers, currency_code), `ItineraryPriceResponse` (search_id, proposal_id, flight_results, stay_results, car_redirect_url, car_redirect_label, provider_status, warnings); import reused schemas from `src.app.schemas.search`
- [ ] T004 [P] Create `src/app/data/cost_bands.py` — define `COST_BANDS` dict structured as `{region_key: {season: {component: (low_usd, high_usd), car_needed: bool}}}`; seed with three entries: "vancouver-island" (flight_per_pax: (300,700), stay_per_night: (150,400), car_per_day: (60,120), car_needed: True), "new-england" (flight_per_pax: (150,450), stay_per_night: (120,350), car_per_day: (50,100), car_needed: True), "pacific-northwest" (flight_per_pax: (200,500), stay_per_night: (130,350), car_per_day: (55,110), car_needed: True); add `estimate_cost(region_key: str, season: str, travelers: TravelerCounts, duration_nights: int, include_car: bool | None) -> ItineraryCostEstimate` that uses midpoint of bands, scales flight by pax count, stay by nights, car by days; add `destination_to_region_key(destination: str) -> str | None` fuzzy matcher (lowercase substring match against known keys)
- [ ] T005 [P] Extend `src/app/nlp/intent.py` — add three new extraction helpers at module level: (1) `extract_party_size(text: str) -> TravelerCounts | None` — parses "family of three/four", "couple", "solo", "two adults one child", "X adults Y children" patterns using NUMBER_MAP; (2) `extract_budget_range(text: str) -> ClarificationBudgetRange | None` — parses "$X-$Y", "$X to $Y", "between $X and $Y" with numeric cleanup; (3) `extract_candidate_destinations(text: str) -> list[str]` — splits on ", ", " or ", " and " after known destination signal phrases ("like", "including", "such as", "consider"); import `ClarificationBudgetRange` from `src.app.schemas.search` and `TravelerCounts` from same
- [ ] T006 Create `src/app/services/itinerary.py` — define `ItineraryService` class; add stub `async def propose(self, request: ItineraryProposeRequest) -> ItineraryProposeResponse` (returns empty response); add stub `async def price_proposal(self, request: ItineraryPriceRequest) -> ItineraryPriceResponse` (returns empty response); add private `_resolve_propose_request(self, request: ItineraryProposeRequest) -> tuple[TravelerCounts, ClarificationBudgetRange | None, list[str], SearchDateRange | None]` stub; instantiate `itinerary_service = ItineraryService()` at module level

**Checkpoint**: Foundation ready — all user story phases can now proceed.

---

## Phase 3: User Story 1 — Receive Proposed Itinerary Options (Priority: P1) 🎯 MVP

**Goal**: A user submitting a complete itinerary prompt receives 2–4 proposal cards with estimated
cost breakdowns, each clearly showing flight, stay, and car components.

**Independent Test**: `POST /api/v1/itinerary/propose` with the sample prompt returns an
`ItineraryProposeResponse` containing 2–4 proposals, each with a non-zero `cost_estimate.total_estimated`
and `destination` field.

- [ ] T007 [US1] Implement `_resolve_propose_request()` in `src/app/services/itinerary.py` — call `extract_candidate_destinations(request.query)`, `extract_budget_range(request.query)`, `extract_party_size(request.query)`, and existing `extract_intent(request.query)` for travel_window; merge NLP results with any explicitly provided request fields (explicit fields win); apply defaults: if travelers not resolved default to TravelerCounts(adults=2, children=1); if travel_window not resolved default to SearchDateRange(start=date(2026,7,1), end=date(2026,7,7))
- [ ] T008 [US1] Implement `propose()` in `src/app/services/itinerary.py` — call `_resolve_propose_request()`; for each candidate destination call `destination_to_region_key()` then `estimate_cost()`; build `ItineraryProposal` for each with uuid proposal_id, within_budget flag (total_estimated ≤ budget_range.maximum if set), rationale string summarising destination + season + duration; sort by within_budget first then ascending total_estimated; return top 4 (or all if ≤ 4); return proposals in `ItineraryProposeResponse`
- [ ] T009 [US1] Create `src/app/api/v1/itinerary.py` — define `router = APIRouter(prefix="/itinerary", tags=["itinerary"])`; add `@router.post("/propose", response_model=ItineraryProposeResponse) async def propose_itinerary(request: ItineraryProposeRequest) -> ItineraryProposeResponse` that calls `await itinerary_service.propose(request)`; import `itinerary_service` from `src.app.services.itinerary`
- [ ] T010 [US1] Register itinerary router in `src/app/main.py` — add `from src.app.api.v1 import itinerary` and `app.include_router(itinerary.router, prefix=settings.API_V1_STR)` alongside the existing search router
- [ ] T011 [P] [US1] Create `web/src/components/itinerary/ItineraryProposalCard.tsx` — accept props `{ proposal: ItineraryProposal; onSelect: (p: ItineraryProposal) => void }` interface; render: destination as heading, duration_nights + travel_window dates, rationale paragraph, cost breakdown section with three rows (✈ Flight ~$X,XXX / 🏨 Stay ~$X,XXX / 🚗 Car ~$XXX or "Not needed"), total estimated cost with "ESTIMATE" chip badge, within_budget green check or amber "Over budget" note, "Select this trip" button that calls `onSelect(proposal)`; use `~${Math.round(value).toLocaleString()}` formatting for approximate values
- [ ] T012 [P] [US1] Create `web/src/components/itinerary/ItineraryProposalList.tsx` — accept props `{ proposals: ItineraryProposal[]; onSelect: (p: ItineraryProposal) => void; isLoading?: boolean }`; render loading skeleton when `isLoading`; render "No proposals found" empty state when proposals is empty; map proposals to `<ItineraryProposalCard>` components; add section heading "Here are your trip options"
- [ ] T013 [US1] Add itinerary TypeScript types and API call to `web/src/lib/api.ts` — add interfaces: `ItineraryCostEstimate`, `ItineraryProposal`, `ItineraryProposeRequest`, `ItineraryProposeResponse`; add `export async function proposeItinerary(req: ItineraryProposeRequest): Promise<ItineraryProposeResponse>` using `apiClient.post('/itinerary/propose', req).then(r => r.data)`
- [ ] T014 [US1] Add itinerary proposal flow to `web/src/app/page.tsx` — add state `proposals: ItineraryProposal[]`, `isProposalLoading: boolean`; add `handleItinerarySearch(query: string)` that calls `proposeItinerary({ query })` and sets proposals; detect itinerary intent when query contains keywords like "itinerary", "trip options", "what are the best", "budget for" — if detected call `handleItinerarySearch` instead of `handleSearch`; render `<ItineraryProposalList proposals={proposals} onSelect={handleSelectProposal} isLoading={isProposalLoading} />` above or instead of `ResultsDashboard` when proposals is non-empty
- [ ] T015 [P] [US1] Write `src/tests/services/test_itinerary.py` — test `propose()` with sample prompt "Given a total budget of $6000-$7500 for a family of three this summer, considering Vancouver Island, New England, or Pacific Northwest" returns 2–4 proposals; test each proposal has non-null destination, cost_estimate, within_budget; test `estimate_cost("new-england", "summer", TravelerCounts(adults=2,children=1), 7, True)` returns ItineraryCostEstimate with total > 0; test `destination_to_region_key("Vancouver Island")` returns "vancouver-island"
- [ ] T016 [P] [US1] Write `web/src/components/itinerary/__tests__/ItineraryProposalCard.test.tsx` — test renders destination name; test renders "ESTIMATE" badge; test renders "~$" prefix on cost values; test within_budget shows green indicator; test over_budget shows note; test clicking "Select this trip" calls `onSelect` with the proposal object
- [ ] T017 [P] [US1] Write `web/src/components/itinerary/__tests__/ItineraryProposalList.test.tsx` — test renders correct number of cards for given proposals array; test renders loading state when `isLoading=true`; test renders empty state when `proposals=[]`; test onSelect callback is passed through to each card

**Checkpoint**: US1 fully functional — submitting the sample prompt returns 2–4 itinerary proposal
cards with cost breakdowns. Independently testable without US2–US4.

---

## Phase 4: User Story 2 — Choose a Proposal and Retrieve Live Prices (Priority: P1)

**Goal**: After a user selects one proposal, the system fetches real flight and accommodation offers
from live providers and displays them with booking redirect links.

**Independent Test**: `POST /api/v1/itinerary/price` with a valid `ItineraryPriceRequest` (using
a proposal snapshot from US1) returns an `ItineraryPriceResponse` containing at least one result
in `flight_results` or `stay_results` (providers permitting) and a non-empty `provider_status` list.

- [ ] T018 [US2] Implement `price_proposal()` in `src/app/services/itinerary.py` — build `SearchRequest` from `request.proposal_snapshot`: set `query=""`, `destination=proposal.destination`, `date_range=proposal.travel_window`, `travelers=request.travelers`, `inventory=[InventoryType.STAY, InventoryType.FLIGHT]`; call `get_provider_registry()` and fan out to each provider as in the existing search service; collect `FlightSearchResult` and `StaySearchResult` items; if `proposal.needs_car` set `car_redirect_url` to an Expedia car-search deep link and `car_redirect_label="Search car rentals"`; collect `ProviderStatus` from registry; return `ItineraryPriceResponse`
- [ ] T019 [US2] Add `POST /api/v1/itinerary/price` route to `src/app/api/v1/itinerary.py` — `@router.post("/price", response_model=ItineraryPriceResponse) async def price_itinerary(request: ItineraryPriceRequest, db: Session = Depends(get_db)) -> ItineraryPriceResponse` that calls `await itinerary_service.price_proposal(request)`
- [ ] T020 [P] [US2] Create `web/src/components/itinerary/ItineraryPricingResult.tsx` — accept props `{ result: ItineraryPriceResponse; proposal: ItineraryProposal; onBack: () => void }`; render: selected destination heading with "LIVE PRICES" badge, provider status strip (green/red per provider), flight results section (cards per FlightSearchResult with carrier, stops, departure/arrival, price, "Book" link), stay results section (cards per StaySearchResult with title, nightly price, amenities, "Book" link), car rental section when `result.car_redirect_url` is set, warnings list, "Back to options" button that calls `onBack`
- [ ] T021 [US2] Add live pricing types and API call to `web/src/lib/api.ts` — add interfaces: `ItineraryPriceRequest`, `ItineraryPriceResponse`; add `export async function priceItinerary(req: ItineraryPriceRequest): Promise<ItineraryPriceResponse>` using `apiClient.post('/itinerary/price', req).then(r => r.data)`
- [ ] T022 [US2] Wire proposal selection and live pricing in `web/src/app/page.tsx` — add state `selectedProposal: ItineraryProposal | null`, `pricingResult: ItineraryPriceResponse | null`, `isPricingLoading: boolean`; implement `handleSelectProposal(proposal: ItineraryProposal)` that sets `selectedProposal`, calls `priceItinerary({ proposal_id: proposal.proposal_id, proposal_snapshot: proposal, travelers: { adults: 2, children: 1, infants: 0 }, currency_code: 'USD' })`, sets `pricingResult`; render `<ItineraryPricingResult result={pricingResult} proposal={selectedProposal} onBack={() => { setPricingResult(null); setSelectedProposal(null); }} />` when pricingResult is non-null
- [ ] T023 [P] [US2] Write `src/tests/api/test_itinerary.py` — use FastAPI TestClient; test `POST /api/v1/itinerary/propose` with sample prompt returns 200 and `proposals` list with length ≥ 1; test `POST /api/v1/itinerary/price` with mocked provider registry (patch `get_provider_registry` to return a mock provider returning a FlightSearchResult) returns 200 with non-empty `flight_results`; test `POST /api/v1/itinerary/price` with all providers mocked as unavailable still returns 200 (not 500) with empty results and non-empty `provider_status`
- [ ] T024 [P] [US2] Write `web/tests/e2e/itinerary.test.ts` — Playwright test: navigate to `/`; type sample prompt "Given a total budget of $6000-$7500 for a family of three this summer, considering Vancouver Island, New England, or the Pacific Northwest" into search input; submit; wait for `[data-testid="itinerary-proposal-list"]` to appear with at least 2 cards; click "Select this trip" on first card; wait for `[data-testid="itinerary-pricing-result"]` to appear; verify at least one result card or warning is shown; run `checkA11y()` on both the proposal list screen and the pricing result screen

**Checkpoint**: US1 + US2 fully functional — full flow from prompt → proposals → select → live prices
works end to end. US1 and US2 together represent the complete MVP.

---

## Phase 5: User Story 3 — Partial Prompt Triggers Clarification (Priority: P2)

**Goal**: When budget, party size, or travel window are missing from the prompt, the existing
clarification loop activates and asks one question at a time before generating proposals.

**Independent Test**: `POST /api/v1/itinerary/propose` with query "I want to travel somewhere nice
this summer" (no budget, no party size) returns `proposals: []` and a non-null
`clarification_state` with the budget slot in `PENDING` state.

- [ ] T025 [US3] Add `_build_itinerary_clarification_state()` to `src/app/services/itinerary.py` — accept resolved `(travelers, budget_range, candidate_destinations, travel_window)` tuple; check which of budget_range, travelers (if defaulted), travel_window were NOT resolved from NLP (vs supplied default); for each missing slot build a `ClarificationSlotState` with state `PENDING`; use existing `SLOT_PROMPTS` from `src.app.services.clarification`; return `ClarificationState` if any slots missing, else `None`
- [ ] T026 [US3] Update `propose()` in `src/app/services/itinerary.py` — call `_build_itinerary_clarification_state()` after `_resolve_propose_request()`; if clarification_state is not None, return `ItineraryProposeResponse(session_id=str(uuid4()), proposals=[], clarification_state=clarification_state, applied_inputs={}, warnings=[])`; handle incoming `request.clarification_answer` by merging the answered slot value into the resolved params before proposal generation
- [ ] T027 [P] [US3] Extend `src/tests/nlp/test_intent.py` — add: `test_extract_party_size_family_of_three()` → TravelerCounts(adults=2, children=1); `test_extract_party_size_couple()` → TravelerCounts(adults=2); `test_extract_budget_range_dollar_dash()` for "$6000-$7500" → min=6000 max=7500; `test_extract_budget_range_to_syntax()` for "$6,000 to $7,500"; `test_extract_candidate_destinations_or_list()` for "Vancouver Island, New England, or Pacific Northwest" → list of 3; `test_extract_candidate_destinations_empty()` for plain query → empty list
- [ ] T028 [P] [US3] Extend `src/tests/services/test_itinerary.py` — add: `test_propose_missing_budget_returns_clarification()` — call `propose()` with query "I want to travel somewhere nice" (no budget); assert `response.proposals == []` and `response.clarification_state is not None`; `test_propose_with_clarification_answer_resolves_to_proposals()` — build request with `clarification_answer` filling in budget slot; assert proposals returned

**Checkpoint**: US3 functional — incomplete prompts now trigger the clarification loop rather than
returning empty proposals silently.

---

## Phase 6: User Story 4 — Cost Breakdown Visible and Understandable (Priority: P2)

**Goal**: Each proposal card renders a clear, labeled, approximate cost breakdown; live pricing
result is visually distinguished from estimates.

**Independent Test**: Render `<ItineraryProposalCard>` with a mock proposal where `needs_car=false`.
Verify: three breakdown rows present (flight, stay, no car row), all cost values prefixed with "~",
"ESTIMATE" badge visible, no "Car" row shown.

- [ ] T029 [US4] Update `web/src/components/itinerary/ItineraryProposalCard.tsx` — refine cost breakdown to render three explicitly labeled rows with icons: "✈ Flight" row showing `~$X,XXX` (flight_estimated), "🏨 Stay" row showing `~$X,XXX` (stay_estimated), "🚗 Car" row showing `~$XXX` (car_estimated) only when `proposal.needs_car` is true OR explicit "Not needed" note when false; add confidence badge (LOW/MED/HIGH) derived from `cost_estimate.confidence`; add `data-testid="proposal-card-{proposal.proposal_id}"` for E2E targeting
- [ ] T030 [P] [US4] Update `web/src/components/itinerary/ItineraryPricingResult.tsx` — add "LIVE PRICE" chip badge to each flight and stay result card; add a summary strip at top showing "Estimated: ~$X,XXX → Live total: $X,XXX (from available offers)" using sum of all returned result prices vs proposal estimate; add `data-testid="itinerary-pricing-result"` on root element; add `data-testid="itinerary-proposal-list"` to `ItineraryProposalList.tsx` root element (needed by E2E in T024)

**Checkpoint**: US4 functional — cost estimates are clearly labeled approximate, live prices are
clearly distinguished, and E2E selectors are in place.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Regression safety, API discoverability, and final verification.

- [ ] T031 [P] Extend `src/tests/test_main.py` — add: test that `POST /api/v1/itinerary/propose` is reachable (returns 200 or 422, not 404); test that `POST /api/v1/itinerary/price` is reachable; test that `GET /health` still returns healthy after new router registration
- [ ] T032 [P] Run `pytest --cov=src --cov-report=term-missing` from repo root — verify all existing tests pass; confirm new test files in `src/tests/services/test_itinerary.py`, `src/tests/api/test_itinerary.py`, and `src/tests/nlp/test_intent.py` are collected and pass; fix any import errors
- [ ] T033 [P] Run `cd web && npm run lint && npm run build` — verify no TypeScript errors in new component files or `api.ts` additions; fix any type mismatches or missing interface fields
- [ ] T034 Update `README.md` Quick Start section — add two new curl examples: one for `POST /api/v1/itinerary/propose` with the sample family prompt, one for `POST /api/v1/itinerary/price` with a placeholder proposal_id; add note that itinerary flow requires Duffel or Amadeus credentials for live pricing step

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 — no dependencies on US2–US4
- **US2 (Phase 4)**: Depends on Phase 2 + US1 (needs itinerary service class from T006, routes from T009/T010, and frontend state from T014)
- **US3 (Phase 5)**: Depends on Phase 2 + US1 — can run after US1 independently of US2
- **US4 (Phase 6)**: Depends on US1 + US2 (updates components created in both phases)
- **Polish (Phase 7)**: Depends on all prior phases

### Within Each Phase

- T003–T006 (Foundational): T003 before T006 (service imports schemas); T004 and T005 parallel with each other
- T007 before T008 (resolve before generate); T009 before T010 (router before registration)
- T011 and T012 parallel (different files); T013 before T014 (types before page wires)
- T018 before T019 (implement before route); T020 parallel with T021

### Parallel Opportunities

All tasks marked [P] within the same phase can run simultaneously. Key parallelism:

```bash
# Phase 2: All four run in parallel
T003 (schemas) + T004 (cost_bands) + T005 (NLP helpers) + T006 (service skeleton)

# Phase 3 backend + frontend in parallel once T006 done:
T007→T008→T009→T010 (backend chain)
T011 + T012 (frontend components, parallel with each other AND with backend chain)
T015 + T016 + T017 (tests, parallel with each other)

# Phase 4:
T018→T019 (backend chain)
T020 + T021 (frontend, parallel with backend chain)
T023 + T024 (tests, parallel with each other)
```

---

## Implementation Strategy

### MVP First (US1 + US2 only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (**critical — blocks everything**)
3. Complete Phase 3: US1 — Proposal generation
4. **STOP and validate**: `curl -X POST .../itinerary/propose` with sample prompt → see 2–4 proposals
5. Complete Phase 4: US2 — Live pricing
6. **STOP and validate**: Select a proposal → see real flight + stay results

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. Phase 3 (US1) → Proposal cards visible in UI → Demo-ready
3. Phase 4 (US2) → Full propose→select→live price flow → **MVP complete**
4. Phase 5 (US3) → Partial prompts handled gracefully
5. Phase 6 (US4) → Cost breakdown polished
6. Phase 7 → Regression clean, docs updated

---

## Notes

- [P] tasks within the same phase = different files, no dependencies on each other
- [Story] label maps task to specific user story for independent delivery traceability
- T024 (E2E) requires a running full stack — run `docker compose up --build` first
- `data-testid` attributes added in T029/T030 are required for T024 to pass — ensure T024 runs after T029/T030
- Car redirect in `price_proposal()` (T018) follows the same Expedia redirect pattern used by `ExpediaRedirectProvider` — no new credentials required
