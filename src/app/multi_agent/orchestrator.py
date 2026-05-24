from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from src.app.multi_agent.agents import (
    DestinationIdeationAgent,
    IntakeClarifierAgent,
    ItineraryBuilderAgent,
    PolicyTrustAgent,
    PresenterAgent,
    PricingAvailabilityAgent,
)
from src.app.multi_agent.interfaces import Agent, AgentRunResult
from src.app.multi_agent.state import deep_merge, new_state
from src.app.multi_agent.store import ConversationStateStore
from src.app.multi_agent.validator import TravelStateValidator


@dataclass
class OrchestratorResult:
    state: dict[str, Any]
    state_patch: dict[str, Any]
    output: str
    executed_agents: list[str]
    response_type: str


class Orchestrator:
    def __init__(
        self,
        schema_path: str | Path,
        state_store: ConversationStateStore | None = None,
    ):
        self.validator = TravelStateValidator(schema_path)
        self.state_store = state_store or ConversationStateStore()
        self.intake = IntakeClarifierAgent()
        self.ideation = DestinationIdeationAgent()
        self.pricing = PricingAvailabilityAgent()
        self.itinerary = ItineraryBuilderAgent()
        self.policy = PolicyTrustAgent()
        self.presenter = PresenterAgent()

    def run(self, state: dict[str, Any] | None, user_message: str) -> OrchestratorResult:
        raw_state = state or {}
        working_state = deep_merge(new_state(), raw_state)
        working_state = deep_merge(working_state, self._extract_user_updates(user_message))
        cumulative_patch: dict[str, Any] = {}
        executed: list[str] = []
        response_type = "questions"

        if self._missing_basics(raw_state, working_state):
            working_state, cumulative_patch = self._run_agent(
                self.intake,
                working_state,
                user_message,
                cumulative_patch,
                executed,
            )
            response_type = "questions"
        else:
            if not working_state.get("candidate_destinations"):
                working_state, cumulative_patch = self._run_agent(
                    self.ideation,
                    working_state,
                    user_message,
                    cumulative_patch,
                    executed,
                )
                response_type = "ideas"

            has_quotes = bool(working_state.get("quotes", {}).get("packages"))
            if not has_quotes:
                working_state, cumulative_patch = self._run_agent(
                    self.pricing,
                    working_state,
                    user_message,
                    cumulative_patch,
                    executed,
                )
                response_type = "packages"

            has_quotes = bool(working_state.get("quotes", {}).get("packages"))
            if has_quotes:
                working_state, cumulative_patch = self._run_agent(
                    self.itinerary,
                    working_state,
                    user_message,
                    cumulative_patch,
                    executed,
                )
                response_type = "itineraries"

        working_state, cumulative_patch = self._run_agent(
            self.policy,
            working_state,
            user_message,
            cumulative_patch,
            executed,
        )
        presenter_result = self.presenter.run(working_state, user_message)
        executed.append(self.presenter.name)
        markdown = str(presenter_result.output.get("markdown", ""))

        self.validator.validate(working_state)
        return OrchestratorResult(
            state=working_state,
            state_patch=cumulative_patch,
            output=markdown,
            executed_agents=executed,
            response_type=response_type,
        )

    @staticmethod
    def _extract_user_updates(user_message: str) -> dict[str, Any]:
        updates: dict[str, Any] = {}
        msg = user_message or ""
        lower = msg.lower()

        date_match = re.search(r"(\d{4}-\d{2}-\d{2}).*?(\d{4}-\d{2}-\d{2})", msg)
        if date_match:
            updates["date_window"] = {
                "start": date_match.group(1),
                "end": date_match.group(2),
            }

        adults_match = re.search(r"\bfor\s+(\d+)\s+(?:adult|adults|people|traveler|travelers)\b", lower)
        if adults_match:
            updates["travelers"] = {"adults": int(adults_match.group(1))}

        budget_match = re.search(r"\$?\s?(\d+(?:\.\d+)?)\s*([kK]?)\s*(?:budget|max)?", lower)
        if "budget" in lower and budget_match:
            max_budget = float(budget_match.group(1))
            if budget_match.group(2):
                max_budget *= 1000
            updates["budget"] = {"max": int(max_budget)}

        length_match = re.search(r"\b(\d{1,2})\s*(?:day|days|night|nights)\b", lower)
        if length_match:
            updates["trip_length_days"] = int(length_match.group(1))

        origin_match = re.search(
            r"\bfrom\s+([a-zA-Z\s]{2,60}?)(?:\s+(?:to|for|on|between|with)\b|$|[.,])",
            msg,
        )
        if origin_match:
            origin_text = origin_match.group(1).strip()
            updates["origin"] = {"city": origin_text.title()}

        return updates

    def run_turn(self, session_id: str, user_message: str) -> OrchestratorResult:
        persisted_state = self.state_store.load(session_id)
        result = self.run(persisted_state, user_message)
        self.state_store.save(session_id, result.state)
        return result

    def _run_agent(
        self,
        agent: Agent,
        state: dict[str, Any],
        user_message: str,
        cumulative_patch: dict[str, Any],
        executed: list[str],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        result: AgentRunResult = agent.run(state, user_message)
        next_state = deep_merge(state, result.state_patch)
        next_patch = deep_merge(cumulative_patch, result.state_patch)
        executed.append(agent.name)
        return next_state, next_patch

    @staticmethod
    def _missing_basics(raw_state: dict[str, Any], state: dict[str, Any]) -> bool:
        raw_origin = raw_state.get("origin")
        origin = state.get("origin", {})
        missing_origin = (
            raw_origin is None
            or (not origin.get("city") and not origin.get("airport"))
        )

        raw_date = raw_state.get("date_window")
        date_window = state.get("date_window", {})
        missing_date = (
            raw_date is None
            or not date_window.get("start")
            or not date_window.get("end")
        )

        raw_travelers = raw_state.get("travelers")
        travelers = state.get("travelers", {})
        missing_travelers = (
            raw_travelers is None or int(travelers.get("adults", 0)) < 1
        )
        return missing_origin or missing_date or missing_travelers
