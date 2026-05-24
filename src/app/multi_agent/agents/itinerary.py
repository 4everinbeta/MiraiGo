from __future__ import annotations

from typing import Any

from src.app.multi_agent.interfaces import AgentRunResult
from src.app.multi_agent.llm import GroqReasoner


class ItineraryBuilderAgent:
    name = "itinerary"

    def __init__(self, reasoner: GroqReasoner | None = None):
        self.reasoner = reasoner or GroqReasoner()

    def run(self, state: dict[str, Any], user_message: str) -> AgentRunResult:
        fallback_itineraries: list[dict[str, Any]] = []
        pace = state.get("preferences", {}).get("pace", "balanced")
        quotes = state.get("quotes", {}).get("packages", [])[:3]
        for package in quotes:
            destination = package.get("destination", "Destination")
            fallback_itineraries.append(
                {
                    "title": f"{destination} {pace.title()} Escape",
                    "destination": destination,
                    "package_id": package.get("id"),
                    "summary": f"A {pace} pace itinerary matched to the selected package tier.",
                    "day_by_day": [
                        {"day": 1, "items": ["Arrival and neighborhood orientation", "Local dinner"]},
                        {"day": 2, "items": ["Signature activity", "Flexible evening block"]},
                        {"day": 3, "items": ["Culture + food highlights", "Departure prep"]},
                    ],
                    "optional_add_ons": ["Airport transfer", "Travel insurance"],
                    "fit_notes": ["Built from package pricing without modifying quoted totals."],
                }
            )
        llm_result = self.reasoner.complete_json(
            system_prompt=(
                "You are ItineraryAgent. Return JSON with `itineraries` as a list of 2-4 itinerary objects. "
                "Preserve package_id links and do not create prices."
            ),
            user_prompt=(
                f"Current state: {state}\n"
                f"Latest user message: {user_message}\n"
                f"Fallback itineraries: {fallback_itineraries}"
            ),
            fallback={"itineraries": fallback_itineraries},
        )
        itineraries = llm_result.get("itineraries", fallback_itineraries)
        if not isinstance(itineraries, list):
            itineraries = fallback_itineraries
        return AgentRunResult(
            state_patch={"itineraries": itineraries},
            output={"itineraries": itineraries},
        )
