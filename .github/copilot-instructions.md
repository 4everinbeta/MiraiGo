# Copilot Instructions — Multi-Agent Travel Planner

## Goal
Generate a multi-agent, tool-enabled AI travel planning system that:
- accepts vague travel intent
- asks minimal follow-up questions
- proposes destinations
- fetches live pricing via tool adapters (no fake prices)
- generates 2–4 itineraries with pricing and disclaimers

## Non-Negotiables
- Do NOT fabricate prices, availability, airline/hotel names, or partnerships.
- All pricing MUST come from tool adapters (stubs are OK initially, but must be clearly marked as TODO).
- The Orchestrator is the only component that “talks” to the user.
- Agents communicate using structured JSON that conforms to `/state/travel-state.schema.json`.

## Architecture
- Multi-agent design with these roles:
  - Orchestrator (user-facing)
  - Intake & Clarifier Agent
  - Destination Ideation Agent
  - Pricing & Availability Agent (tool-using)
  - Itinerary Builder Agent
  - Policy/Trust Agent
  - Presenter Agent
- Shared state object persisted between turns.
- Routing rules:
  1) Missing origin/date/travelers → Intake questions
  2) Have basics but no destinations → Ideation
  3) Have destinations + basics → Pricing calls
  4) Have quotes → Itinerary options
  5) Validate via Policy/Trust
  6) Format via Presenter

## Implementation Expectations
- Produce clean interfaces for agents: `run(state, userMessage) -> { statePatch, output }`
- Provide deterministic JSON outputs for specialist agents.
- Include example conversation flows and unit tests.
- Add tool adapters:
  - `searchFlights(...)`
  - `searchHotels(...)`
  - `buildPackage(...)`
  These can be stubs with realistic response shapes, but must never return invented values without marking as mocked.

## Formatting and UX
- Orchestrator output headings:
  - Quick Questions (if needed)
  - Top Picks
  - Packages & Live Pricing
  - Sample Itineraries
  - Next Tweaks
- Always include:
  - pricing retrieval timestamp
  - inclusions/exclusions
  - “prices subject to change”