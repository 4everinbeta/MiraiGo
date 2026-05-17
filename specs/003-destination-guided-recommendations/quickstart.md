# Quickstart — Destination Guided Recommendations

## Goal

Validate destination-guided clarification, preference capture, comparison recommendations, flight-first alternatives, and lodging follow-through in local development.

## Prerequisites

1. `.env` configured from `.env.example`
2. Docker available for full-stack run
3. Optional provider credentials configured for live inventory tests

## Run locally

1. Start full stack:
   - `docker compose up --build`
2. Open web app:
   - `http://localhost:3000`
3. Confirm API health/docs:
   - `http://localhost:8000/docs`

## Manual validation flow

1. Submit a destination-missing prompt, e.g.:
   - “I want a warm beach trip in July for 3 on a moderate budget”
2. Verify first follow-up asks for location narrowing and presents suggestions.
3. Choose “don’t care” and verify curated popular picks appear.
4. Select one destination, then repeat with multiple destinations and verify comparison mode.
5. Answer follow-ups: trip length, budget, flexibility, travel preferences.
6. Verify recommendation bundles include explicit rationale.
7. Trigger live shopping and verify:
   - Flight options shown first
   - Nearby-date price alternatives shown
   - Lodging options shown after route/date context is selected
8. Simulate partial provider availability and verify graceful warnings without flow failure.

## Test commands

1. Backend tests:
   - `PYTHONPATH=. ./venv/bin/pytest -q src/tests/nlp src/tests/services src/tests/api`
2. Frontend unit tests:
   - `cd web && npm test -- --runInBand`
3. Frontend E2E:
   - `cd web && npm run test:e2e`

## Expected artifacts

- Updated plan: `specs/003-destination-guided-recommendations/plan.md`
- Research: `specs/003-destination-guided-recommendations/research.md`
- Data model: `specs/003-destination-guided-recommendations/data-model.md`
- Contract: `specs/003-destination-guided-recommendations/contracts/search-clarification-contract.md`
