from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class AgentRunResult:
    state_patch: dict[str, Any]
    output: dict[str, Any]


class Agent(Protocol):
    name: str

    def run(self, state: dict[str, Any], user_message: str) -> AgentRunResult:
        ...

