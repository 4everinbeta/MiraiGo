from __future__ import annotations

from pydantic import BaseModel, Field


class OrchestratorTurnRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=2000)


class OrchestratorTurnResponse(BaseModel):
    session_id: str
    response_type: str
    markdown: str
    open_questions: list[str] = Field(default_factory=list)
    candidate_destinations: list[dict] = Field(default_factory=list)
    packages: list[dict] = Field(default_factory=list)
    itineraries: list[dict] = Field(default_factory=list)
    disclaimers: list[str] = Field(default_factory=list)
    executed_agents: list[str] = Field(default_factory=list)
