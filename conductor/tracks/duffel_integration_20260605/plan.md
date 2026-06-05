# Plan: Duffel Flight Provider Integration

This plan executes the robust integration, data mapping refinement, and error handling for the Duffel flights provider.

## Phase 1: Complete Duffel Data Mapping [checkpoint: a383471]

* **TDD - Response Fields Mapping**
  * - [x] Task: Write failing pytest unit/integration tests in `src/tests/providers/test_duffel.py` verifying that all expected fields (`price_minor`, `currency_code`, `duration_minutes`, `stops_count`) are parsed from the Duffel response and mapped to `FlightSearchResult`. [419d187]
  * - [x] Task: Update the response mapping in `src/app/scrapers/duffel.py` (or the Duffel provider) to match the fields correctly. Verify that unit tests pass. [419d187]

* **Phase Verification**
  * - [ ] Task: Conductor - User Manual Verification 'Phase 1: Complete Duffel Data Mapping' (Protocol in workflow.md)

---

## Phase 2: Error Handling, Timeouts, and Fallbacks

* **TDD - Timeout and Configuration Fallbacks**
  * - [x] Task: Write failing pytest unit/integration tests in `src/tests/providers/test_duffel.py` asserting that request timeouts trigger retries and that missing configuration/credentials gracefully transition search state to degraded with appropriate `no_flight_guidance`. [c1401e1]
  * - [x] Task: Implement HTTP retry logic, credentials validation, and health checks reporting in the Duffel provider. Verify that all tests pass. [c1401e1]

* **Phase Verification**
  * - [ ] Task: Conductor - User Manual Verification 'Phase 2: Error Handling, Timeouts, and Fallbacks' (Protocol in workflow.md)
