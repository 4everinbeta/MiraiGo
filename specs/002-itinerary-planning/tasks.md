---

description: "Task list for Itinerary Proposal with Estimated and Live Pricing"
---

# Tasks: Itinerary Proposal with Estimated and Live Pricing

**Input**: Design documents from `specs/002-itinerary-planning/`

**Prerequisites**: plan.md (required), spec.md (required), data-model.md (available)

**Tests**: Included because the spec explicitly requires backend, frontend, and E2E coverage.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unresolved dependency)
- **[Story]**: User story label (US1, US2, US3, US4)
- Every task includes an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure expected module paths and directories exist for new itinerary code.

- [ ] T001 Create backend package marker in `src/app/data/__init__.py`
- [ ] T002 [P] Create itinerary component directory placeholder in `web/src/components/itinerary/.gitkeep`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared data contracts and core service scaffolding required by all stories.

**⚠️ CRITICAL**: No user story implementation starts before this phase is complete.

- [ ] T003 Create itinerary schemas in `src/app/schemas/itinerary.py`
- [ ] T004 [P] Create destination cost band lookup utilities in `src/app/data/cost_bands.py`
- [ ] T005 [P] Extend itinerary-related NLP extraction helpers in `src/app/nlp/intent.py`
- [ ] T006 Create itinerary service skeleton in `src/app/services/itinerary.py`
- [ ] T007 Create itinerary router scaffold with propose/price endpoints in `src/app/api/v1/itinerary.py`
- [ ] T008 Register itinerary router in `src/app/main.py`

**Checkpoint**: Shared schema, NLP, service, and route foundations are ready.

---

## Phase 3: User Story 1 - Receive Proposed Itinerary Options (Priority: P1) 🎯 MVP

**Goal**: Return 2–4 destination proposals with clear estimated cost breakdowns from a natural-language prompt.

**Independent Test**: Submit the sample prompt and verify 2–4 proposals with destination + estimated breakdown fields.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add propose-service behavior tests in `src/tests/services/test_itinerary.py`
- [ ] T010 [P] [US1] Add propose API endpoint tests in `src/tests/api/test_itinerary.py`
- [ ] T011 [P] [US1] Add proposal card component tests in `web/src/components/itinerary/__tests__/ItineraryProposalCard.test.tsx`
- [ ] T012 [P] [US1] Add proposal list component tests in `web/src/components/itinerary/__tests__/ItineraryProposalList.test.tsx`

### Implementation for User Story 1

- [ ] T013 [US1] Implement request-resolution logic for propose flow in `src/app/services/itinerary.py`
- [ ] T014 [US1] Implement itinerary proposal generation and ranking in `src/app/services/itinerary.py`
- [ ] T015 [US1] Implement `/itinerary/propose` handler wiring in `src/app/api/v1/itinerary.py`
- [ ] T016 [P] [US1] Implement proposal card UI in `web/src/components/itinerary/ItineraryProposalCard.tsx`
- [ ] T017 [P] [US1] Implement proposal list UI in `web/src/components/itinerary/ItineraryProposalList.tsx`
- [ ] T018 [US1] Add propose API types and client function in `web/src/lib/api.ts`
- [ ] T019 [US1] Wire proposal-search flow state and rendering in `web/src/app/page.tsx`

**Checkpoint**: US1 works independently end-to-end for proposal generation.

---

## Phase 4: User Story 2 - Choose a Proposal and Retrieve Live Prices (Priority: P1)

**Goal**: Let users select a proposal and retrieve real provider-backed pricing results.

**Independent Test**: Select one proposal and verify live price response contains provider status and at least one flight/stay result or warning.

### Tests for User Story 2

- [ ] T020 [P] [US2] Add live-pricing API tests (including graceful degradation) in `src/tests/api/test_itinerary.py`
- [ ] T021 [P] [US2] Add proposal-to-pricing E2E flow test in `web/tests/e2e/itinerary.test.ts`

### Implementation for User Story 2

- [ ] T022 [US2] Implement live pricing orchestration in `src/app/services/itinerary.py`
- [ ] T023 [US2] Implement `/itinerary/price` handler wiring in `src/app/api/v1/itinerary.py`
- [ ] T024 [P] [US2] Implement pricing result UI in `web/src/components/itinerary/ItineraryPricingResult.tsx`
- [ ] T025 [US2] Add price API types and client function in `web/src/lib/api.ts`
- [ ] T026 [US2] Wire proposal selection and pricing state in `web/src/app/page.tsx`

**Checkpoint**: US2 works independently once a proposal is available.

---

## Phase 5: User Story 3 - Partially Specified Prompt Triggers Clarification (Priority: P2)

**Goal**: Reuse existing clarification loop for missing budget, travelers, or travel window before proposal generation.

**Independent Test**: Submit an incomplete itinerary prompt and verify clarification state is returned instead of proposals.

### Tests for User Story 3

- [ ] T027 [P] [US3] Add itinerary NLP extraction tests for party size, budget range, and destination list in `src/tests/nlp/test_intent.py`
- [ ] T028 [P] [US3] Add clarification-loop service tests in `src/tests/services/test_itinerary.py`

### Implementation for User Story 3

- [ ] T029 [US3] Implement itinerary clarification-state builder in `src/app/services/itinerary.py`
- [ ] T030 [US3] Merge clarification answers into proposal resolution flow in `src/app/services/itinerary.py`

**Checkpoint**: US3 works independently for incomplete prompts.

---

## Phase 6: User Story 4 - Cost Breakdown is Visible and Understandable (Priority: P2)

**Goal**: Make estimated vs live pricing distinctions explicit and visually clear in UI.

**Independent Test**: Render proposal and pricing views and verify labeled estimate/live badges plus car-needed behavior.

### Tests for User Story 4

- [ ] T031 [P] [US4] Extend itinerary component tests for estimate/live labeling in `web/src/components/itinerary/__tests__/ItineraryProposalCard.test.tsx`
- [ ] T032 [P] [US4] Extend itinerary component tests for pricing summary and status indicators in `web/src/components/itinerary/__tests__/ItineraryProposalList.test.tsx`

### Implementation for User Story 4

- [ ] T033 [US4] Refine proposal breakdown rendering and test IDs in `web/src/components/itinerary/ItineraryProposalCard.tsx`
- [ ] T034 [US4] Refine pricing-result estimate-vs-live summary and test IDs in `web/src/components/itinerary/ItineraryPricingResult.tsx`
- [ ] T035 [US4] Add itinerary proposal list root test ID in `web/src/components/itinerary/ItineraryProposalList.tsx`

**Checkpoint**: US4 independently satisfies clarity and UX labeling requirements.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Finish system-level validation, docs, and regression confidence.

- [ ] T036 [P] Add itinerary route availability checks in `src/tests/test_main.py`
- [ ] T037 [P] Validate backend suite and coverage command in `src/tests/`
- [ ] T038 [P] Validate frontend lint/build path in `web/`
- [ ] T039 Update itinerary quickstart API examples in `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US2)**: Depends on Phase 2 and US1
- **Phase 5 (US3)**: Depends on Phase 2 and US1
- **Phase 6 (US4)**: Depends on US1 and US2
- **Phase 7 (Polish)**: Depends on all story phases

### User Story Completion Order

1. **US1 (P1)** — MVP proposal generation
2. **US2 (P1)** — MVP live pricing on selection
3. **US3 (P2)** — Clarification loop for incomplete prompts
4. **US4 (P2)** — Pricing clarity and UX polish

---

## Parallel Execution Examples

### User Story 1

```bash
# Parallel test work
T009 + T010 + T011 + T012

# Parallel UI work after API contracts exist
T016 + T017
```

### User Story 2

```bash
# Parallel implementation
T024 + T025

# Parallel validation
T020 + T021
```

### User Story 3

```bash
# Parallel test authoring
T027 + T028
```

### User Story 4

```bash
# Parallel test updates
T031 + T032
```

---

## Implementation Strategy

### MVP First (Suggested Scope)

1. Complete Phase 1 + Phase 2
2. Complete Phase 3 (US1)
3. Complete Phase 4 (US2)
4. Validate propose → select → live price flow

### Incremental Delivery

1. Deliver US1 (proposal generation)
2. Add US2 (live pricing)
3. Add US3 (clarification robustness)
4. Add US4 (cost clarity and UX)
5. Finish Phase 7 polish tasks

