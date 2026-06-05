# Multi-Agent Travel Planner — Architecture

## Overview
A tool-enabled AI travel planning system that transforms vague intent into bookable options with live pricing. The Orchestrator is the only user-facing component; specialist agents produce structured JSON updates.

## Agents
1) Orchestrator (user-facing)
2) Intake & Clarifier Agent
3) Destination Ideation Agent
4) Pricing & Availability Agent (tool-using)
5) Itinerary Builder Agent
6) Policy/Trust Agent
7) Presenter Agent

## Shared State
All agents read/write a shared state object that conforms to `/state/travel-state.schema.json`.

## Routing Rules
- If missing origin/date/travelers → Intake
- If no candidate_destinations → Ideation
- If candidates exist and basics exist → Pricing
- If quotes exist → Itinerary
- Then validate via Policy/Trust
- Then format via Presenter

## Output Constraints
- No fabricated pricing or availability.
- Pricing must include retrieval timestamp and inclusions/exclusions.
- Always disclose “prices subject to change”.

## Tool Adapters (Pricing)
- searchFlights(origin, destination, date_window, travelers, constraints)
- searchHotels(destination, date_window, rooms, preferences)
- buildPackage(flightId, hotelId)

Adapters can be stubs initially but MUST clearly mark mocked responses and never claim “live pricing” unless actually live.

## UX
Orchestrator’s user response headings:
- Quick Questions (if needed)
- Top Picks
- Packages & Live Pricing
- Sample Itineraries
- Next Tweaks