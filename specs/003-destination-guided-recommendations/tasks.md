# Tasks: Destination Guided Recommendations

**Input**: Design documents from `/specs/003-destination-guided-recommendations/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included. This feature requires backend, frontend unit, and E2E validation per constitution and quickstart.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish baseline scaffolding and documentation links for this feature implementation.

**Phase Gate (Behavioral Tests First)**: Define and pass unit + integration behavioral tests for setup acceptance before setup implementation tasks.

- [X] T045 [P] Add Phase 1 behavioral unit test gate for setup contract invariants in src/tests/schemas/test_search_schemas.py
- [X] T046 [P] Add Phase 1 behavioral integration/API gate for additive contract compatibility in src/tests/api/test_search.py
- [X] T001 Create implementation task baseline in specs/003-destination-guided-recommendations/tasks.md
- [X] T002 [P] Add feature-specific API type placeholders in web/src/lib/api.ts
- [X] T003 [P] Add feature-specific backend schema placeholders in src/app/schemas/search.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core structures required before any user story implementation.

**⚠️ CRITICAL**: No user story work starts before this phase completes.
**Phase Gate (Behavioral Tests First)**: Define and pass unit + integration behavioral tests for foundational acceptance before foundational implementation tasks.

- [X] T047 [P] Add Phase 2 behavioral unit test gate for clarification/session baseline behavior in src/tests/services/test_clarification_loop.py
- [X] T048 [P] Add Phase 2 behavioral integration/API gate for foundational clarification response behavior in src/tests/api/test_search.py
- [X] T004 Extend clarification slot/state models for destination suggestion payloads in src/app/schemas/search.py
- [X] T005 Implement shared suggestion builder utilities for destination narrowing in src/app/services/clarification.py
- [X] T006 Add request/response compatibility handling for new additive contract fields in src/app/services/search.py
- [X] T007 [P] Add frontend rendering primitives for suggestion options and multi-select chips in web/src/components/search/SearchForm.tsx
- [X] T008 [P] Add frontend request/response mapping for new contract fields in web/src/lib/api.ts
- [X] T009 Add foundational regression tests for additive schema compatibility in src/tests/schemas/test_search_schemas.py

**Checkpoint**: Foundation ready for independent user story implementation.

---

## Phase 3: User Story 1 - Guided destination narrowing when destination is missing (Priority: P1) 🎯 MVP

**Goal**: Users without a destination get destination-first suggestions, including “don’t care” curated picks and optional multi-destination selection.

**Independent Test**: Submit destination-missing intent and verify destination-first follow-up with selectable suggestions and “don’t care” curated options.

### Tests for User Story 1

- [ ] T010 [P] [US1] Add parser coverage for destination-missing prompt classification in src/tests/nlp/test_intent.py
- [ ] T011 [P] [US1] Add clarification loop tests for destination suggestion emission and “don’t care” handling in src/tests/services/test_clarification_loop.py
- [ ] T012 [P] [US1] Add API tests for destination_suggestions response payload in src/tests/api/test_search.py
- [ ] T013 [P] [US1] Add SearchForm unit tests for suggestion rendering/selection in web/src/components/search/__tests__/ClarificationFlow.test.tsx

### Implementation for User Story 1

- [ ] T014 [US1] Implement backend destination suggestion generation and ranking hooks in src/app/services/search.py
- [ ] T015 [US1] Implement “don’t care” curated popular destination fallback in src/app/services/search.py
- [ ] T016 [US1] Wire suggestion fields to API response contracts in src/app/api/v1/search.py
- [ ] T017 [US1] Implement suggestion list, “don’t care”, and multi-select interactions in web/src/components/search/SearchForm.tsx
- [ ] T018 [US1] Persist destination selection mode/candidates in page-level session state in web/src/app/page.tsx
- [ ] T019 [US1] Ensure additive type safety for destination_suggestions and destination_candidates in web/src/lib/api.ts

**Checkpoint**: US1 is independently functional and testable (MVP slice).

---

## Phase 4: User Story 2 - Preference-aware recommendation packaging (Priority: P2)

**Goal**: Collect richer preferences (flexibility, flight constraints, trip style) and produce rationale-backed recommendation bundles with comparison support.

**Independent Test**: After destination selection, complete preference follow-ups and verify ranked recommendation packages with comparison-ready dimensions.

### Tests for User Story 2

- [ ] T020 [P] [US2] Add service tests for preference capture and recap update behavior in src/tests/services/test_clarification_loop.py
- [ ] T021 [P] [US2] Add service tests for recommendation bundle generation and rationale fields in src/tests/services/test_search_dual_provider.py
- [ ] T022 [P] [US2] Add API tests for recommendation_packages payload in src/tests/api/test_search.py
- [ ] T023 [P] [US2] Add frontend unit tests for preference follow-up inputs and recap edits in web/src/components/search/__tests__/ClarificationFlow.test.tsx

### Implementation for User Story 2

- [ ] T024 [US2] Extend constraint_updates parsing for date_flexibility, flight_preferences, and trip_style_tags in src/app/schemas/search.py
- [ ] T025 [US2] Implement preference profile assembly and recommendation package scoring in src/app/services/search.py
- [ ] T026 [US2] Add recommendation package payload fields to response schemas in src/app/schemas/search.py
- [ ] T027 [US2] Render recommendation package cards and comparison context in web/src/components/search/ResultsDashboard.tsx
- [ ] T028 [US2] Add preference follow-up controls and payload submission wiring in web/src/components/search/SearchForm.tsx
- [ ] T029 [US2] Persist and merge preference fields in turn session resolution in web/src/app/page.tsx

**Checkpoint**: US2 works independently with recommendation packaging and comparison.

---

## Phase 5: User Story 3 - Flight-first live shopping with lodging follow-through (Priority: P3)

**Goal**: Present live flight options first with nearby-date alternatives, then lodging aligned to selected flight/date context.

**Independent Test**: Choose destination(s), trigger live shopping, review flight-first alternatives, select context, then verify lodging categories for that context.

### Tests for User Story 3

- [ ] T030 [P] [US3] Add service tests for nearby-date flight alternatives and ordering in src/tests/services/test_search_dual_provider.py
- [ ] T031 [P] [US3] Add API tests for flight_options and lodging_options additive payloads in src/tests/api/test_search.py
- [ ] T032 [P] [US3] Add frontend unit tests for flight-first rendering and lodging follow-through state in web/src/components/search/__tests__/ResultsDashboard.test.tsx
- [ ] T033 [P] [US3] Add E2E scenario for destination compare → flight-first → lodging follow-through with @axe-core/playwright accessibility checks on all primary pages in web/tests/e2e/clarification.spec.ts

### Implementation for User Story 3

- [ ] T034 [US3] Implement flight option grouping with nearby-date alternatives in src/app/services/search.py
- [ ] T035 [US3] Implement lodging option grouping by category for selected context in src/app/services/search.py
- [ ] T036 [US3] Add additive flight_options and lodging_options response models in src/app/schemas/search.py
- [ ] T037 [US3] Surface flight-first grouped alternatives in web/src/components/search/ResultsDashboard.tsx
- [ ] T038 [US3] Add lodging category display tied to selected flight/date context in web/src/components/search/ResultsDashboard.tsx
- [ ] T039 [US3] Update API client types/mapping for new live shopping groups in web/src/lib/api.ts

**Checkpoint**: US3 is independently functional for flight-first + lodging follow-through.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality and cross-story stabilization.

- [ ] T040 [P] Update product copy and helper text for clarity/consistency in web/src/components/search/SearchForm.tsx
- [ ] T041 [P] Add/refresh warning messaging for partial provider availability in web/src/components/search/ResultsDashboard.tsx
- [ ] T042 Run backend targeted suite for this feature in src/tests/
- [ ] T043 Run frontend unit and E2E scenarios for this feature in web/tests/e2e/ and web/src/components/search/__tests__/
- [ ] T044 Update quickstart verification notes after implementation in specs/003-destination-guided-recommendations/quickstart.md
- [ ] T049 [P] Add service + API tests asserting each recommendation bundle exposes ≥3 comparison dimensions (total_cost, flight_duration, trip_tone_match) in src/tests/services/test_search_dual_provider.py and src/tests/api/test_search.py
- [ ] T050 [P] Verify preference recap is visible and editable before final recommendation generation (unit test for recap state in web/src/components/search/__tests__/ClarificationFlow.test.tsx)
- [ ] T051 [P] Add E2E test asserting the full destination → preference → recommendation flow completes within ≤3 clarification turns (FR-016 criterion a) — assert turn counter ≤3 at recommendations-rendered state in web/tests/e2e/clarification.spec.ts

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately; Phase 1 implementation tasks depend on T045 + T046 behavioral gate tests.
- **Phase 2 (Foundational)**: Depends on Phase 1; foundational implementation tasks depend on T047 + T048 behavioral gate tests; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; defines MVP.
- **Phase 4 (US2)**: Depends on Phase 2 and integrates with US1 state model.
- **Phase 5 (US3)**: Depends on Phase 2 and consumes US1/US2 context fields.
- **Phase 6 (Polish)**: Depends on completion of selected stories (minimum US1 for MVP, US1+US2+US3 for full scope).

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories; primary MVP.
- **US2 (P2)**: Independent after foundational work, but reuses destination candidates from US1 when available.
- **US3 (P3)**: Independent after foundational work, but expected to use resolved preferences from US2 for best relevance.

### Within Each User Story

- Tests first (TDD-style), then implementation.
- Schema/model updates before service logic.
- Service logic before API/UI wiring.
- UI rendering after response contract fields are available.

### Parallel Opportunities

- Phase 1: T045 and T046 parallel first; T002 and T003 parallel after phase gate tests pass.
- Phase 2: T047 and T048 parallel first; T007, T008, T009 parallel after T004–T006 baseline.
- US1: T010–T013 parallel; T017 and T019 parallel after backend contract fields exist.
- US2: T020–T023 parallel; T027 and T028 parallel after T024–T026.
- US3: T030–T033 parallel; T037 and T038 parallel after T034–T036.
- Polish: T040 and T041 parallel.

---

## Parallel Example: User Story 1

```bash
# Parallel test authoring for US1
Task: "T010 [US1] src/tests/nlp/test_intent.py"
Task: "T011 [US1] src/tests/services/test_clarification_loop.py"
Task: "T012 [US1] src/tests/api/test_search.py"
Task: "T013 [US1] web/src/components/search/__tests__/ClarificationFlow.test.tsx"

# Parallel UI/API typing after backend fields exist
Task: "T017 [US1] web/src/components/search/SearchForm.tsx"
Task: "T019 [US1] web/src/lib/api.ts"
```

## Parallel Example: User Story 2

```bash
# Parallel tests for preference/recommendation behavior
Task: "T020 [US2] src/tests/services/test_clarification_loop.py"
Task: "T021 [US2] src/tests/services/test_search_dual_provider.py"
Task: "T022 [US2] src/tests/api/test_search.py"
Task: "T023 [US2] web/src/components/search/__tests__/ClarificationFlow.test.tsx"
```

## Parallel Example: User Story 3

```bash
# Parallel tests for live shopping group behavior
Task: "T030 [US3] src/tests/services/test_search_dual_provider.py"
Task: "T031 [US3] src/tests/api/test_search.py"
Task: "T032 [US3] web/src/components/search/__tests__/ResultsDashboard.test.tsx"
Task: "T033 [US3] web/tests/e2e/clarification.spec.ts"
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) fully.
3. Validate destination-first guidance and “don’t care” popular picks.
4. Demo/review before proceeding.

### Incremental Delivery

1. Add US2 preference packaging and comparison recommendations.
2. Add US3 flight-first/lodging follow-through.
3. Finish polish, run full targeted validation.

### Suggested MVP Scope

- **MVP**: Phase 1 + Phase 2 + Phase 3 (T001–T019).
- **Post-MVP**: Phase 4–6 for full competitive differentiation.

---

## Notes

- Tasks touching the same file are intentionally sequenced unless marked [P].
- All API changes are additive to preserve existing clients.
- Keep provider-failure graceful degradation behavior intact throughout implementation.
