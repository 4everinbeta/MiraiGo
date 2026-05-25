from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from src.app.multi_agent.orchestrator import Orchestrator
from src.app.schemas.orchestration import OrchestratorTurnRequest, OrchestratorTurnResponse
from src.app.services.search import SearchService

router = APIRouter()

_SCHEMA_PATH = Path(__file__).resolve().parents[4] / "state" / "travel-state.schema.json"
_ORCHESTRATOR = Orchestrator(schema_path=_SCHEMA_PATH)
_SEARCH_SERVICE = SearchService()


@router.post("/orchestrator/turn", response_model=OrchestratorTurnResponse)
async def orchestrator_turn(payload: OrchestratorTurnRequest) -> OrchestratorTurnResponse:
    result = _ORCHESTRATOR.run_turn(payload.session_id, payload.message)
    state = result.state
    quotes = state.get("quotes", {})

    search_response = None
    if payload.search_payload is not None:
        try:
            search_response = await _SEARCH_SERVICE.search(payload.search_payload)
        except Exception:
            search_response = None

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
        search_response=search_response,
    )
