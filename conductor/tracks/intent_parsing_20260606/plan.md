# Plan: Improved Search Intent Parsing

This plan details the implementation of improved search intent parsing, origin-destination confusion guard, and expanded destination discovery suggestions.

## Phase 1: Implement Intent Parser Improvements [checkpoint: b4c1ea5]

* **TDD - Intent Parsing Refinement**
  * - [x] Task: Write failing pytest unit tests in `src/tests/nlp/test_intent_refinement.py` asserting that queries like "Flights in July from Denver" correctly extract Denver as the origin rather than the destination, and that relative/month queries resolve correctly. [1367b07]
  * - [x] Task: Update the intent parsing implementation in `src/app/nlp/intent.py` and destination suggestion list in `src/app/services/search.py` to pass the tests. Verify that all unit tests pass. [38f9d5c]

* **Phase Verification**
  * - [x] Task: Conductor - User Manual Verification 'Phase 1: Implement Intent Parser Improvements' (Protocol in workflow.md) [b4c1ea5]
