from __future__ import annotations

from pathlib import Path

import pytest

from src.app.multi_agent.orchestrator import Orchestrator
from src.app.multi_agent.state import new_state
from src.app.multi_agent.validator import StateValidationError, TravelStateValidator


SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "state" / "travel-state.schema.json"
)


def build_ready_state() -> dict:
    state = new_state()
    state["user_intent"] = "Beach trip with airfare options"
    state["origin"] = {"city": "Seattle", "airport": "SEA"}
    state["date_window"] = {"start": "2026-07-10", "end": "2026-07-15", "flexible_days": 2}
    state["travelers"] = {"adults": 2, "children": 0, "child_ages": []}
    return state


def test_missing_origin_routes_to_intake() -> None:
    orchestrator = Orchestrator(SCHEMA_PATH)
    state = build_ready_state()
    state["origin"] = {"city": "", "airport": ""}

    result = orchestrator.run(state, "Plan my summer trip")

    assert result.executed_agents[0] == "intake"


def test_missing_candidates_routes_to_ideation() -> None:
    orchestrator = Orchestrator(SCHEMA_PATH)
    state = build_ready_state()
    state["candidate_destinations"] = []

    result = orchestrator.run(state, "Need destination ideas")

    assert "ideation" in result.executed_agents


def test_candidates_present_routes_to_pricing() -> None:
    orchestrator = Orchestrator(SCHEMA_PATH)
    state = build_ready_state()
    state["candidate_destinations"] = [
        {
            "destination": "Lisbon, Portugal",
            "why_it_fits": ["Warm weather"],
            "best_for": ["food"],
            "risk_notes": ["Crowds"],
        }
    ]
    state["quotes"] = {"retrieved_at": "", "currency": "USD", "packages": []}

    result = orchestrator.run(state, "Price this option")

    assert "pricing" in result.executed_agents


def test_quotes_present_routes_to_itinerary() -> None:
    orchestrator = Orchestrator(SCHEMA_PATH)
    state = build_ready_state()
    state["candidate_destinations"] = [
        {
            "destination": "Lisbon, Portugal",
            "why_it_fits": ["Warm weather"],
            "best_for": ["food"],
            "risk_notes": ["Crowds"],
        }
    ]
    state["quotes"] = {
        "retrieved_at": "2026-05-24T12:00:00Z",
        "currency": "USD",
        "packages": [
            {
                "id": "pkg-lisbon-1",
                "destination": "Lisbon, Portugal",
                "total_price": 1200,
                "is_mocked": True,
            }
        ],
    }

    result = orchestrator.run(state, "Build itinerary")

    assert "itinerary" in result.executed_agents
    assert "pricing" not in result.executed_agents


def test_policy_runs_before_presenter() -> None:
    orchestrator = Orchestrator(SCHEMA_PATH)
    state = build_ready_state()

    result = orchestrator.run(state, "Plan trip")

    policy_idx = result.executed_agents.index("policy_trust")
    presenter_idx = result.executed_agents.index("presenter")
    assert policy_idx < presenter_idx


def test_run_turn_persists_state_between_turns() -> None:
    orchestrator = Orchestrator(SCHEMA_PATH)
    first = orchestrator.run_turn(
        "session-a",
        "Plan a 5 day trip from Denver for 2 adults with budget 4500 between 2026-08-10 and 2026-08-16",
    )
    second = orchestrator.run_turn("session-a", "Continue")

    assert first.state["origin"]["city"] == "Denver"
    assert second.state["origin"]["city"] == "Denver"
    assert second.response_type in {"ideas", "packages", "itineraries"}


def test_policy_includes_subject_to_change_disclaimer() -> None:
    orchestrator = Orchestrator(SCHEMA_PATH)
    result = orchestrator.run(build_ready_state(), "Plan trip")

    disclaimers = result.state.get("user_visible_disclaimers", [])
    assert any("subject to change" in text.lower() for text in disclaimers)


def test_schema_validator_accepts_default_state() -> None:
    validator = TravelStateValidator(SCHEMA_PATH)
    validator.validate(new_state())


def test_schema_validator_rejects_invalid_state() -> None:
    validator = TravelStateValidator(SCHEMA_PATH)
    invalid = new_state()
    invalid.pop("origin")

    with pytest.raises(StateValidationError):
        validator.validate(invalid)
