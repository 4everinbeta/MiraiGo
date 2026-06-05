# Build Multi-Agent Travel Planner

## Goal
Generate a multi-agent travel planner with an Orchestrator and 6 specialist agents, using the shared state schema.

## Context
Use /docs/architecture.md, /agents/*.md, and /state/travel-state.schema.json as the source of truth.

## Expectations
- Implement in a clean, modular way.
- Provide agent interfaces and routing logic.
- Provide stub tool adapters for pricing.
- Provide unit tests for routing decisions and JSON schema validation.

## Task
1) Create an `Agent` interface: run(state, userMessage) => { statePatch, output }
2) Implement Orchestrator routing policy as described.
3) Implement each specialist agent returning deterministic JSON.
4) Implement Pricing tool adapters as stubs returning MOCKED data clearly labeled.
5) Add a validator to ensure state conforms to JSON schema.
6) Add tests: missing origin triggers Intake; missing candidates triggers Ideation; presence triggers Pricing; quotes trigger Itinerary; always runs Policy/Trust before Presenter.