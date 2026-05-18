---

description: "Task list for Improve Post-Intent Suggestions"
---

# Tasks: Improve Post-Intent Suggestions

**Input**: Design documents from `/specs/005-improve-suggestions/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/suggestion-quality-contract.md, quickstart.md

**Tests**: Included. This feature explicitly requires behavioral coverage and phase-gated unit + integration checks.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no unresolved dependency)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`) for story phases only
- Each task includes an explicit file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature-specific scaffolding and test placeholders.

- [ ] T001 Create feature task file scaffold in `specs/005-improve-suggestions/tasks.md`
- [ ] T002 [P] Create backend unit test module for suggestion quality in `src/tests/services/test_suggestion_quality.py`
- [ ] T003 [P] Create backend integration test module for suggestion contract behavior in `src/tests/api/test_suggestion_quality.py`
- [ ] T004 [P] Create frontend suggestion behavior test module in `web/src/components/search/__tests__/SuggestionQuality.test.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared primitives required by all stories: fit metadata, deterministic guardrails, and session continuity hooks.

**⚠️ CRITICAL**: No user story work starts until this phase is complete.

- [ ] T005 Extend suggestion/clarification schemas for fit and rationale metadata in `src/app/schemas/search.py`
- [ ] T006 Add deterministic hard-blocker evaluation helper in `src/app/services/search.py`
- [ ] T007 Add duplicate-signature generation helper in `src/app/services/search.py`
- [ ] T008 Add suggestion rationale assembly helper in `src/app/services/search.py`
- [ ] T009 Add session continuity merge helper for resolved slots in `src/app/services/search.py`
- [ ] T010 [P] Add baseline backend tests for new shared helpers in `src/tests/services/test_suggestion_quality.py`

**Checkpoint**: Shared model and helper layer is ready for independent user-story delivery.

---

## Phase 3: User Story 1 - More Relevant Suggestions (Priority: P1) 🎯 MVP

**Goal**: Return top suggestions that satisfy destination + timeline + budget hard blockers and include explicit rationale.

**Independent Test**: Submit a fully specified intent and verify top 3 suggestions satisfy hard blockers, with rationale and over-budget labels when needed.

### Tests for User Story 1

- [ ] T011 [P] [US1] Add hard-blocker ranking tests in `src/tests/services/test_suggestion_quality.py`
- [ ] T012 [P] [US1] Add API response tests for rationale and hard-constraint labels in `src/tests/api/test_suggestion_quality.py`
- [ ] T013 [P] [US1] Add UI rendering tests for rationale sentence and reason tags in `web/src/components/search/__tests__/SuggestionQuality.test.tsx`

### Implementation for User Story 1

- [ ] T014 [US1] Implement destination+timeline+budget hard-blocker gating before ranking in `src/app/services/search.py`
- [ ] T015 [US1] Implement top-3 suggestion selection and partial-fit labeling in `src/app/services/search.py`
- [ ] T016 [US1] Implement rationale payload composition (one sentence + 2-3 tags) in `src/app/services/search.py`
- [ ] T017 [US1] Wire suggestion fit/rationale fields into API response shaping in `src/app/services/search.py`
- [ ] T018 [US1] Render rationale sentence and reason tags in suggestions UI in `web/src/components/search/ResultsDashboard.tsx`
- [ ] T019 [US1] Render explicit partial-fit/over-budget markers in suggestions UI in `web/src/components/search/ResultsDashboard.tsx`

**Checkpoint**: US1 independently delivers relevant, explained top suggestions.

---

## Phase 4: User Story 2 - Stable Multi-Turn Suggestion Quality (Priority: P1)

**Goal**: Preserve resolved constraints across turns and stop repeated-slot clarification loops unless user edits.

**Independent Test**: Start from partial prompt, answer follow-ups, and confirm resolved slots persist while next question advances correctly.

### Tests for User Story 2

- [ ] T020 [P] [US2] Add multi-turn slot-preservation tests for answer flow in `src/tests/services/test_clarification_loop.py`
- [ ] T021 [P] [US2] Add no-repeat-slot regression tests after valid follow-up answers in `src/tests/services/test_clarification_loop.py`
- [ ] T022 [P] [US2] Add API-level multi-turn continuity test in `src/tests/api/test_suggestion_quality.py`

### Implementation for User Story 2

- [ ] T023 [US2] Update clarification turn merge to preserve prior resolved constraints by default in `src/app/services/search.py`
- [ ] T024 [US2] Restrict slot reopening to explicit recap edits and constraint updates in `src/app/services/search.py`
- [ ] T025 [US2] Add loop-guard counter and repeated-question protection in `src/app/services/search.py`
- [ ] T026 [US2] Ensure frontend turn session preserves applied filters and clarification state across submissions in `web/src/app/page.tsx`
- [ ] T027 [US2] Ensure recap chip edits trigger targeted refresh without resetting unrelated resolved constraints in `web/src/components/search/SearchForm.tsx`

**Checkpoint**: US2 independently stabilizes clarification progression and suggestion continuity.

---

## Phase 5: User Story 3 - Actionable Suggestion Transparency (Priority: P2)

**Goal**: Make suggestion explanations actionable, support recap edits cleanly, and allow guarded LLM-assisted suggestion generation.

**Independent Test**: Edit recap constraints and verify refreshed suggestions/rationale reflect new constraints; confirm LLM outputs are post-validated before display.

### Tests for User Story 3

- [ ] T028 [P] [US3] Add recap-edit refresh tests for stale rationale prevention in `src/tests/services/test_suggestion_quality.py`
- [ ] T029 [P] [US3] Add duplicate-suppression tests for near-identical candidate outputs in `src/tests/services/test_suggestion_quality.py`
- [ ] T030 [P] [US3] Add LLM-output guardrail tests (hard-blocker post-validation) in `src/tests/services/test_suggestion_quality.py`

### Implementation for User Story 3

- [ ] T031 [US3] Implement semantic duplicate suppression by signature in `src/app/services/search.py`
- [ ] T032 [US3] Integrate optional LLM-assisted suggestion generation behind deterministic post-validation in `src/app/services/search.py`
- [ ] T033 [US3] Surface “why shown” transparency details in results display cards in `web/src/components/search/ResultsDashboard.tsx`

**Checkpoint**: US3 independently delivers transparent suggestions, safe LLM assist, and deduplicated outputs.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final reliability, performance guardrails, and end-to-end confidence.

- [ ] T034 [P] Add end-to-end suggestion quality journey test in `web/tests/e2e/search.test.ts`
- [ ] T035 [P] Add quickstart validation notes for manual checks in `specs/005-improve-suggestions/quickstart.md`
- [ ] T036 [P] Update API route tests for non-regression of existing search behavior in `src/tests/api/test_search.py`
- [ ] T037 Run backend feature test suites and fix regressions in `src/tests/`
- [ ] T038 Run frontend unit/E2E suites and fix regressions in `web/src/components/search/__tests__/` and `web/tests/e2e/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories
- **Phase 3 (US1)**: Depends on Phase 2
- **Phase 4 (US2)**: Depends on Phase 2 and US1 response shaping primitives
- **Phase 5 (US3)**: Depends on Phase 2 and US1; integrates with US2 continuity behavior
- **Phase 6 (Polish)**: Depends on all story phases

### User Story Dependencies

- **US1 (P1)**: First MVP increment (relevance + rationale)
- **US2 (P1)**: Second MVP increment (continuity + loop prevention)
- **US3 (P2)**: Third increment (transparency depth + LLM guardrails + dedupe)

### Within Each User Story

- Tests first (failing expectations) before implementation
- Backend ranking/continuity logic before UI rendering updates
- API response shaping before frontend consumption assertions

---

## Parallel Execution Examples

### User Story 1

```bash
# Parallel tests
T011 + T012 + T013

# Parallel UI work after T017
T018 + T019
```

### User Story 2

```bash
# Parallel regression coverage
T020 + T021 + T022
```

### User Story 3

```bash
# Parallel test-first work
T028 + T029 + T030
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Setup + Foundational
2. Deliver US1 relevance and rationale contract
3. Deliver US2 multi-turn stability and loop protection
4. Validate with quickstart scenarios before US3

### Incremental Delivery

1. US1: Better top suggestions with explicit rationale
2. US2: Stable follow-up progression without repeated-slot loops
3. US3: Advanced transparency, dedupe, and guarded LLM suggestion assist
4. Polish: E2E and regression hardening

