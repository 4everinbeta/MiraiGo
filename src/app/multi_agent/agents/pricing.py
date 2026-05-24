from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.app.multi_agent.adapters import PricingAdapters
from src.app.multi_agent.interfaces import AgentRunResult


class PricingAvailabilityAgent:
    name = "pricing"

    def __init__(self, adapters: PricingAdapters | None = None):
        self.adapters = adapters or PricingAdapters()

    def run(self, state: dict[str, Any], user_message: str) -> AgentRunResult:
        candidates = state.get("candidate_destinations", [])[:4]
        packages: list[dict[str, Any]] = []
        budget_currency = state.get("budget", {}).get("currency") or "USD"

        for candidate in candidates:
            destination = candidate.get("destination", "")
            flights = self.adapters.search_flights(
                origin=state.get("origin", {}),
                destination=destination,
                date_window=state.get("date_window", {}),
                travelers=state.get("travelers", {}),
                constraints=state.get("constraints", {}),
            )
            hotels = self.adapters.search_hotels(
                destination=destination,
                date_window=state.get("date_window", {}),
                rooms=max(1, state.get("travelers", {}).get("adults", 1) // 2 or 1),
                preferences=state.get("preferences", {}),
            )
            tier_pairs = list(zip(flights[:2], hotels[:2]))
            for index, (flight, hotel) in enumerate(tier_pairs, start=1):
                package_link = self.adapters.build_package(flight["id"], hotel["id"])
                total_price = flight["total_price"] + hotel["total_price"]
                adults = max(1, state.get("travelers", {}).get("adults", 1))
                is_mocked = bool(flight.get("is_mocked") or hotel.get("is_mocked"))
                packages.append(
                    {
                        "id": f"pkg-{destination.lower().replace(' ', '-')}-{index}",
                        "destination": destination,
                        "flight": flight,
                        "hotel": hotel,
                        "total_price": total_price,
                        "price_per_traveler": round(total_price / adults, 2),
                        "included": [
                            "Roundtrip flight",
                            "Hotel stay",
                        ],
                        "excluded": [
                            "Taxes and destination fees where applicable",
                            "Optional upgrades",
                        ],
                        "cancellation_terms": (
                            "MOCKED policy: flexible cancellation up to 72h before departure."
                            if is_mocked
                            else "Cancellation terms vary by supplier and fare brand."
                        ),
                        "links_or_ids": package_link,
                        "is_mocked": is_mocked,
                    }
                )

        quotes = {
            "retrieved_at": datetime.now(UTC).isoformat(),
            "currency": budget_currency,
            "packages": packages,
        }
        assumptions = list(state.get("assumptions", []))
        if any(package.get("is_mocked") for package in packages):
            assumptions.append("Some pricing is generated from MOCKED stub adapters (not live inventory).")
        return AgentRunResult(
            state_patch={
                "quotes": quotes,
                "assumptions": assumptions,
            },
            output={"quotes": quotes},
        )
