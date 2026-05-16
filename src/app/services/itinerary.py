from __future__ import annotations

from datetime import date

from src.app.data.cost_bands import destination_to_region_key, estimate_cost
from src.app.nlp.intent import (
    extract_budget_range,
    extract_candidate_destinations,
    extract_intent,
    extract_party_size,
)
from src.app.schemas.itinerary import (
    ItineraryProposal,
    ItineraryPriceRequest,
    ItineraryPriceResponse,
    ItineraryProposeRequest,
    ItineraryProposeResponse,
)
from src.app.schemas.search import ClarificationBudgetRange, SearchDateRange, TravelerCounts


class ItineraryService:
    async def propose(self, request: ItineraryProposeRequest) -> ItineraryProposeResponse:
        """Generate 2–4 itinerary proposals with static cost estimates."""
        travelers, budget_range, candidates, travel_window = self._resolve_propose_request(request)

        proposals: list[ItineraryProposal] = []
        season = self._detect_season(travel_window)

        for destination in candidates:
            region_key = destination_to_region_key(destination)
            if not region_key:
                continue

            cost = estimate_cost(
                region_key=region_key,
                season=season,
                travelers=travelers,
                duration_nights=self._duration_nights(travel_window),
                include_car=request.include_car,
            )

            within_budget = True
            over_budget_note: str | None = None
            if budget_range and budget_range.maximum:
                within_budget = cost.total_estimated <= budget_range.maximum
                if not within_budget:
                    over_budget_note = (
                        f"Estimated total ${cost.total_estimated:,.0f} "
                        f"exceeds your budget of ${budget_range.maximum:,.0f}"
                    )

            rationale = (
                f"{destination} in {season.capitalize()} for {travelers.adults} adults"
                + (f" and {travelers.children} children" if travelers.children else "")
                + f" over {self._duration_nights(travel_window)} nights"
                + (" — car recommended for this destination" if cost.car_estimated > 0 else "")
            )

            proposals.append(
                ItineraryProposal(
                    destination=destination,
                    destination_region_key=region_key,
                    travel_window=travel_window,
                    duration_nights=self._duration_nights(travel_window),
                    travelers=travelers,
                    needs_car=cost.car_estimated > 0,
                    cost_estimate=cost,
                    rationale=rationale,
                    within_budget=within_budget,
                    over_budget_note=over_budget_note,
                )
            )

        # Sort: within budget first, then ascending total estimated cost
        proposals.sort(key=lambda p: (not p.within_budget, p.cost_estimate.total_estimated))
        top_proposals = proposals[:4]

        applied_inputs: dict = {
            "travelers": travelers.model_dump(),
            "travel_window": {
                "start": travel_window.start.isoformat(),
                "end": travel_window.end.isoformat() if travel_window.end else None,
            },
            "budget_range": budget_range.model_dump() if budget_range else None,
            "candidates": candidates,
        }

        return ItineraryProposeResponse(
            proposals=top_proposals,
            applied_inputs=applied_inputs,
        )

    async def price_proposal(self, request: ItineraryPriceRequest) -> ItineraryPriceResponse:
        """Fetch live prices for a selected proposal via provider adapters."""
        # Stub: live provider fan-out implemented in T018
        return ItineraryPriceResponse(
            proposal_id=request.proposal_id,
        )

    def _resolve_propose_request(
        self,
        request: ItineraryProposeRequest,
    ) -> tuple[TravelerCounts, ClarificationBudgetRange | None, list[str], SearchDateRange]:
        """Merge NLP-extracted values with any explicitly provided request fields."""
        # Explicit fields win over NLP extraction
        travelers = request.travelers or extract_party_size(request.query) or TravelerCounts(adults=2, children=1)

        budget_range = request.budget_range or extract_budget_range(request.query)

        candidates = request.candidate_destinations or extract_candidate_destinations(request.query)

        travel_window = request.travel_window
        if not travel_window:
            intent = extract_intent(request.query)
            date_range = intent.get("date_range")
            if date_range and date_range.get("start"):
                travel_window = SearchDateRange(
                    start=date.fromisoformat(date_range["start"]),
                    end=date.fromisoformat(date_range["end"]) if date_range.get("end") else None,
                )
        if not travel_window:
            travel_window = SearchDateRange(start=date(2026, 7, 1), end=date(2026, 7, 7))

        return travelers, budget_range, candidates, travel_window

    def _duration_nights(self, travel_window: SearchDateRange) -> int:
        if travel_window.end:
            return max(1, (travel_window.end - travel_window.start).days)
        return 7  # default when only start date is known

    def _detect_season(self, travel_window: SearchDateRange) -> str:
        month = travel_window.start.month
        if month in (12, 1, 2):
            return "winter"
        if month in (3, 4, 5):
            return "spring"
        if month in (6, 7, 8):
            return "summer"
        return "fall"


itinerary_service = ItineraryService()
