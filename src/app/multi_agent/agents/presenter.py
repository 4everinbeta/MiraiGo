from __future__ import annotations

from typing import Any

from src.app.multi_agent.interfaces import AgentRunResult
from src.app.multi_agent.llm import GroqReasoner


class PresenterAgent:
    name = "presenter"

    def __init__(self, reasoner: GroqReasoner | None = None):
        self.reasoner = reasoner or GroqReasoner()

    def run(self, state: dict[str, Any], user_message: str) -> AgentRunResult:
        open_questions = state.get("open_questions", [])
        candidates = state.get("candidate_destinations", [])[:4]
        packages = state.get("quotes", {}).get("packages", [])[:4]
        itineraries = state.get("itineraries", [])[:4]
        disclaimers = state.get("user_visible_disclaimers", [])
        retrieved_at = state.get("quotes", {}).get("retrieved_at", "unknown")

        lines: list[str] = []
        if open_questions:
            lines.append("## Quick Questions")
            for question in open_questions:
                lines.append(f"- {question}")
            lines.append("")

        if candidates:
            lines.append("## Top Picks")
            for candidate in candidates:
                lines.append(f"- **{candidate['destination']}** — {candidate['why_it_fits'][0]}")
            lines.append("")

        lines.append("## Packages & Live Pricing")
        lines.append(f"- Retrieval time: `{retrieved_at}`")
        if packages:
            for package in packages:
                lines.append(
                    f"- **{package['destination']}** · `{package['id']}` · "
                    f"{state['quotes']['currency']} {package['total_price']}"
                    f"{' (MOCKED)' if package.get('is_mocked') else ''}"
                )
        else:
            lines.append("- No priced packages yet.")
        lines.append("")

        if itineraries:
            lines.append("## Sample Itineraries")
            for itinerary in itineraries:
                lines.append(f"- **{itinerary['title']}** ({itinerary['package_id']})")
        else:
            lines.append("## Sample Itineraries")
            lines.append("- Itineraries will appear after package pricing is available.")
        lines.append("")

        lines.append("## Next Tweaks")
        lines.append("- Cheaper total")
        lines.append("- Prefer nonstop")
        lines.append("- Nicer hotel")
        lines.append("- Different vibe")
        lines.append("")

        if disclaimers:
            lines.append("### Disclaimers")
            for disclaimer in disclaimers:
                lines.append(f"- {disclaimer}")

        fallback_markdown = "\n".join(lines).strip()
        llm_result = self.reasoner.complete_json(
            system_prompt=(
                "You are PresenterAgent. Return JSON with key `markdown`, formatting a clean user-facing travel response. "
                "Do not invent prices, availability, or timestamps."
            ),
            user_prompt=(
                f"Current state: {state}\n"
                f"Latest user message: {user_message}\n"
                f"Fallback markdown: {fallback_markdown}"
            ),
            fallback={"markdown": fallback_markdown},
        )
        markdown = str(llm_result.get("markdown", fallback_markdown))
        return AgentRunResult(
            state_patch={},
            output={"markdown": markdown},
        )
