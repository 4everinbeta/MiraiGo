from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.app.multi_agent.interfaces import AgentRunResult


class PolicyTrustAgent:
    name = "policy_trust"

    def run(self, state: dict[str, Any], user_message: str) -> AgentRunResult:
        issues_found: list[str] = []
        required_disclaimers: list[str] = []
        edits: list[str] = []
        quotes = state.get("quotes", {})
        retrieved_at = quotes.get("retrieved_at")
        if not retrieved_at:
            issues_found.append("Missing pricing retrieval timestamp.")
            retrieved_at = datetime.now(UTC).isoformat()
        required_disclaimers.append("Prices are subject to change until booking is confirmed.")

        packages = quotes.get("packages", [])
        if any(not package.get("is_mocked") for package in packages):
            edits.append("Add source provenance for non-mocked prices.")
        if any(package.get("is_mocked") for package in packages):
            required_disclaimers.append(
                "Pricing shown here is MOCKED stub data for development and not live inventory."
            )
        return AgentRunResult(
            state_patch={
                "quotes": {"retrieved_at": retrieved_at} if quotes else {},
                "user_visible_disclaimers": required_disclaimers,
            },
            output={
                "issues_found": issues_found,
                "required_disclaimers": required_disclaimers,
                "edits": edits,
            },
        )
