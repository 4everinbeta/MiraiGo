from __future__ import annotations

from typing import Any

from src.app.multi_agent.interfaces import AgentRunResult
from src.app.multi_agent.llm import GroqReasoner


class IntakeClarifierAgent:
    name = "intake"

    def __init__(self, reasoner: GroqReasoner | None = None):
        self.reasoner = reasoner or GroqReasoner()

    def run(self, state: dict[str, Any], user_message: str) -> AgentRunResult:
        open_questions: list[str] = []
        date_window = state.get("date_window", {})
        origin = state.get("origin", {})
        travelers = state.get("travelers", {})

        if not date_window.get("start") or not date_window.get("end"):
            open_questions.append("What date range are you considering?")
        if not origin.get("city") and not origin.get("airport"):
            open_questions.append("What city or airport are you departing from?")
        if not travelers or travelers.get("adults", 0) < 1:
            open_questions.append("How many travelers should I plan for?")
        if state.get("trip_length_days") in (None, 0):
            open_questions.append("How many days do you want this trip to be?")
        budget = state.get("budget", {})
        if budget.get("max") in (None, 0):
            open_questions.append("What total budget range should I target?")

        llm_result = self.reasoner.complete_json(
            system_prompt=(
                "You are IntakeAgent for a travel planning assistant. "
                "Return JSON with a single key `open_questions` as a concise list (max 3) "
                "of follow-up questions needed to complete missing trip constraints."
            ),
            user_prompt=(
                f"Current state: {state}\n"
                f"Latest user message: {user_message}\n"
                f"Fallback questions: {open_questions[:3]}"
            ),
            fallback={"open_questions": open_questions[:3]},
        )
        resolved_questions = llm_result.get("open_questions", open_questions[:3])
        if not isinstance(resolved_questions, list):
            resolved_questions = open_questions[:3]

        patch = {
            "user_intent": user_message or state.get("user_intent", ""),
            "open_questions": [str(question) for question in resolved_questions[:3]],
        }
        return AgentRunResult(
            state_patch=patch,
            output={
                "open_questions": patch["open_questions"],
            },
        )
