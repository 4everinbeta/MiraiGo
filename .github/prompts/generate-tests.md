# Generate Tests

## Goal
Add robust tests for safety and correctness.

## Expectations
- Validate: no fabricated prices in Presenter output unless marked mocked.
- Validate: required disclaimers are always present when prices exist.
- Validate: JSON schema compliance for all agent outputs.

## Task
Create a test suite covering:
- Intake question priority
- Ideation diversity
- Pricing failure handling
- Itinerary references package_id
- Policy/Trust edits injected into final response