# Plan: Synthesized Expedia Accommodation Provider

This plan details the implementation of synthesized hotel results for the Expedia stays provider.

## Phase 1: Implement Expedia Synthesized Provider [checkpoint: 2319540]

* **TDD - Stays Provider Restructuring**
  * - [x] Task: Write failing pytest unit tests in `src/tests/providers/test_expedia.py` asserting that Expedia provider returns multiple stays (matching beach, mountain, historic, and city profiles) with correct total price calculations, star ratings, and amenities scoring. [e29d8d8]
  * - [x] Task: Convert `ExpediaRedirectProvider` into `ExpediaDemandProvider` in `src/app/providers/expedia.py` and register it in `src/app/providers/registry.py`. Implement the destination-tailored mock generator to satisfy the test assertions. Verify that all unit tests pass. [bcf73e0]

* **Phase Verification**
  * - [x] Task: Conductor - User Manual Verification 'Phase 1: Implement Expedia Synthesized Provider' (Protocol in workflow.md)
