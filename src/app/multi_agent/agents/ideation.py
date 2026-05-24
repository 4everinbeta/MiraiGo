from __future__ import annotations

from typing import Any

from src.app.multi_agent.interfaces import AgentRunResult
from src.app.multi_agent.llm import GroqReasoner


class DestinationIdeationAgent:
    name = "ideation"

    def __init__(self, reasoner: GroqReasoner | None = None):
        self.reasoner = reasoner or GroqReasoner()

    def run(self, state: dict[str, Any], user_message: str) -> AgentRunResult:
        interests = state.get("preferences", {}).get("interests", [])
        interest_label = ", ".join(interests[:2]) if interests else "varied activities"
        fallback_candidates = [
            {
                "destination": "Lisbon, Portugal",
                "why_it_fits": [
                    f"Balanced pace and good fit for {interest_label}.",
                    "Strong value-to-experience ratio for mixed city + coast trips.",
                ],
                "best_for": ["culture", "food", "walkable"],
                "risk_notes": ["Peak-season hotel rates can surge on weekends."],
            },
            {
                "destination": "Cancun, Mexico",
                "why_it_fits": [
                    "Reliable warm-weather option for low-friction planning.",
                    "Wide range of resort tiers for budget control.",
                ],
                "best_for": ["beach", "resort", "family"],
                "risk_notes": ["Storm-season weather variability may impact activities."],
            },
            {
                "destination": "Tokyo, Japan",
                "why_it_fits": [
                    "High-density attractions with strong transport convenience.",
                    "Works well for first-time long-haul planning with clear itineraries.",
                ],
                "best_for": ["city", "food", "shopping"],
                "risk_notes": ["Popular districts can be crowded during peak periods."],
            },
        ]
        llm_result = self.reasoner.complete_json(
            system_prompt=(
                "You are IdeationAgent for travel planning. Return JSON with key "
                "`candidate_destinations` as a list of up to 4 destination objects. "
                "Each object must include: destination, why_it_fits (array), best_for (array), risk_notes (array)."
            ),
            user_prompt=(
                f"Current state: {state}\n"
                f"Latest user message: {user_message}\n"
                f"Fallback candidates: {fallback_candidates}"
            ),
            fallback={"candidate_destinations": fallback_candidates},
        )
        candidates = llm_result.get("candidate_destinations", fallback_candidates)
        if not isinstance(candidates, list):
            candidates = fallback_candidates

        return AgentRunResult(
            state_patch={"candidate_destinations": candidates[:4]},
            output={"candidate_destinations": candidates[:4]},
        )
