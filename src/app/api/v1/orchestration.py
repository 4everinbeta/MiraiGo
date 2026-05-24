from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from src.app.multi_agent.orchestrator import Orchestrator
from src.app.schemas.orchestration import OrchestratorTurnRequest, OrchestratorTurnResponse

router = APIRouter()

_SCHEMA_PATH = Path(__file__).resolve().parents[4] / "state" / "travel-state.schema.json"
_ORCHESTRATOR = Orchestrator(schema_path=_SCHEMA_PATH)


@router.post("/orchestrator/turn", response_model=OrchestratorTurnResponse)
def orchestrator_turn(payload: OrchestratorTurnRequest) -> OrchestratorTurnResponse:
    result = _ORCHESTRATOR.run_turn(payload.session_id, payload.message)
    state = result.state
    quotes = state.get("quotes", {})
    return OrchestratorTurnResponse(
        session_id=payload.session_id,
        response_type=result.response_type,
        markdown=result.output,
        open_questions=state.get("open_questions", []),
        candidate_destinations=state.get("candidate_destinations", []),
        packages=quotes.get("packages", []),
        itineraries=state.get("itineraries", []),
        disclaimers=state.get("user_visible_disclaimers", []),
        executed_agents=result.executed_agents,
    )
