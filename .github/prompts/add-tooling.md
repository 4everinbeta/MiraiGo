# Add Real Pricing Tooling

## Goal
Replace stubs with real travel API integration.

## Context
Pricing agent uses searchFlights/searchHotels/buildPackage.

## Expectations
- Keep pricing truthful: do not claim live unless truly live.
- Cache retrieval timestamp.
- Handle failures gracefully.

## Task
Implement adapters for the chosen API provider and wire into Pricing agent.
Include rate limiting, retries, and error mapping to failure_reason suggestions.