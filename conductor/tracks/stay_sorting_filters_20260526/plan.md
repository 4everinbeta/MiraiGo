# Plan: Interactive Stay Value Sorting and Filters

This plan executes the TDD development, client-side implementation, and visual polish of the stays sorting and filter controls.

## Phase 1: Component & Core UI Logic

* **TDD - Sorting Stays (Red/Green/Refactor)**
  * - [ ] Task: Create failing Jest tests in `web/src/components/search/__tests__/ResultsDashboard.test.tsx` asserting that the stays list re-ranks correctly when score, absolute price, or star ratings sort parameters are set.
  * - [ ] Task: Implement stays sorting dropdown controls and the corresponding client-side array sorting logic in `web/src/components/search/ResultsDashboard.tsx`. Verify that Jest tests pass.

* **TDD - Dynamic Filtering (Red/Green/Refactor)**
  * - [ ] Task: Create failing Jest tests in `web/src/components/search/__tests__/ResultsDashboard.test.tsx` asserting that stays are correctly filtered out by max price threshold, rating star thresholds (e.g. 3+ or 4+ stars), and amenities arrays (e.g. WiFi and Pool).
  * - [ ] Task: Implement the filter control panel (price slider, ratings chips, and amenities checkboxes) and the multi-filter client-side array matching logic in `web/src/components/search/ResultsDashboard.tsx`. Verify that Jest tests pass.

* **Phase Verification**
  * - [ ] Task: Conductor - User Manual Verification 'Phase 1: Component & Core UI Logic' (Protocol in workflow.md)

---

## Phase 2: Premium Visual Polish & Micro-animations

* **E2E & Aesthetics (Red/Green/Refactor)**
  * - [ ] Task: Create a new E2E spec under Playwright in `web/tests/e2e/search.test.ts` (or update it) to write a failing test that simulates adjusting the price slider and toggling amenities filters, asserting that the stays list updates visually.
  * - [ ] Task: Polish the filter panel layout with smooth Tailwind animations/transitions on entry/exit, apply glassmorphic backdrop-blur overlays, and verify that all text/badge elements strictly meet the WCAG 2 AA contrast ratio target (4.5:1). Confirm Playwright E2E tests pass.

* **Phase Verification**
  * - [ ] Task: Conductor - User Manual Verification 'Phase 2: Premium Visual Polish & Micro-animations' (Protocol in workflow.md)
