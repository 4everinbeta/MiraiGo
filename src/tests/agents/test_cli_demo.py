from __future__ import annotations

from pathlib import Path

from src.app.multi_agent.cli_demo import run_turn
from src.app.multi_agent.orchestrator import Orchestrator
from src.app.multi_agent.state import new_state


SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "state" / "travel-state.schema.json"
)


def test_run_turn_returns_markdown_and_persists_state() -> None:
    orchestrator = Orchestrator(SCHEMA_PATH)
    state = new_state()

    updated_state, markdown_1 = run_turn(orchestrator, state, "Plan me a warm beach trip.")
    updated_state["origin"] = {"city": "Denver", "airport": "DEN"}
    updated_state["date_window"] = {
        "start": "2026-08-10",
        "end": "2026-08-16",
        "flexible_days": 1,
    }
    updated_state["travelers"] = {"adults": 2, "children": 0, "child_ages": []}

    persisted_state, markdown_2 = run_turn(
        orchestrator, updated_state, "Continue with options."
    )

    assert "## Packages & Live Pricing" in markdown_1
    assert "## Packages & Live Pricing" in markdown_2
    assert persisted_state["origin"]["airport"] == "DEN"

