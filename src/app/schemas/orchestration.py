from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.app.schemas.search import SearchRequest, SearchResponse


class OrchestratorTurnRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=2000)
    # Optional: include a full typed search payload to execute the search path
    # alongside the orchestrator turn and return typed reliability metadata.
    search_payload: SearchRequest | None = None


class OrchestratorTurnResponse(BaseModel):
    session_id: str
    response_type: str
    markdown: str
    open_questions: list[str] = Field(default_factory=list)
    candidate_destinations: list[dict[str, Any]] = Field(default_factory=list)
    packages: list[dict[str, Any]] = Field(default_factory=list)
    itineraries: list[dict[str, Any]] = Field(default_factory=list)
    disclaimers: list[str] = Field(default_factory=list)
    executed_agents: list[str] = Field(default_factory=list)
    # Optional: typed search result including degraded_state and clarification_state.
    # Populated only when search_payload was provided in the request.
    search_response: SearchResponse | None = None
