from __future__ import annotations

import asyncio
from datetime import date
from urllib.parse import urlencode

from src.app.data.cost_bands import destination_to_region_key, estimate_cost
from src.app.nlp.intent import (
    extract_budget_range,
    extract_candidate_destinations,
    extract_intent,
    extract_party_size,
)
from src.app.providers import get_provider_registry
from src.app.providers.base import ProviderError, TravelProvider
from src.app.schemas.itinerary import (
    ItineraryProposal,
    ItineraryPriceRequest,
    ItineraryPriceResponse,
    ItineraryProposeRequest,
    ItineraryProposeResponse,
)
from src.app.schemas.search import (
    ClarificationBudgetRange,
    ClarificationSlot,
    ClarificationSlotState,
    ClarificationState,
    FlightSearchResult,
    FlightFilters,
    InventoryType,
    ProviderStatus,
    SearchDateRange,
    SearchRequest,
    SearchResult,
    StayFilters,
    StaySearchResult,
    TravelerCounts,
)
from src.app.services.clarification import SLOT_PROMPTS, build_clarification_state


class ItineraryService:
    async def propose(self, request: ItineraryProposeRequest) -> ItineraryProposeResponse:
        """Generate 2–4 itinerary proposals with static cost estimates."""
        travelers, budget_range, candidates, travel_window = self._resolve_propose_request(request)
        intent = extract_intent(request.query)

        if request.clarification_answer and request.clarification_answer.slot == ClarificationSlot.BUDGET:
            budget_from_answer = extract_budget_range(request.clarification_answer.answer_text or "")
            if budget_from_answer:
                budget_range = budget_from_answer

        clarification_state = self._build_itinerary_clarification_state(
            travelers=travelers,
            budget_range=budget_range,
            candidate_destinations=candidates,
            travel_window=travel_window,
            travelers_defaulted=(
                request.travelers is None and extract_party_size(request.query) is None
            ),
            timeline_defaulted=(
                request.travel_window is None
                and not (intent.get("date_range") or {}).get("start")
                and not bool(intent.get("dates"))
            ),
        )
        if clarification_state is not None and request.clarification_answer is None:
            return ItineraryProposeResponse(
                proposals=[],
                clarification_state=clarification_state,
                applied_inputs={},
                warnings=[],
            )

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
            clarification_state=clarification_state,
            applied_inputs=applied_inputs,
        )

    async def price_proposal(self, request: ItineraryPriceRequest) -> ItineraryPriceResponse:
        """Fetch live prices for a selected proposal via provider adapters."""
        proposal = request.proposal_snapshot
        search_request = SearchRequest(
            query="",
            destination=proposal.destination,
            date_range=proposal.travel_window,
            travelers=request.travelers,
            inventory=[InventoryType.STAY, InventoryType.FLIGHT],
            stay_filters=StayFilters(),
            flight_filters=FlightFilters(nonstop=False),
            currency_code=request.currency_code,
        )

        providers = get_provider_registry()
        provider_status = await asyncio.gather(*[provider.healthcheck() for provider in providers])
        status_map: dict[str, ProviderStatus] = {
            status.provider: status for status in provider_status
        }

        warnings: list[str] = []
        results: list[SearchResult] = []
        tasks = [
            self._run_provider_inventory(provider, search_request, inventory_type)
            for provider in providers
            for inventory_type in search_request.inventory
            if provider.supports_inventory(inventory_type)
        ]
        executions = await asyncio.gather(*tasks)
        for provider, _, provider_results, error_message in executions:
            results.extend(provider_results)
            if error_message:
                warnings.append(error_message)
                existing = status_map.get(provider.provider_name)
                if existing:
                    status_map[provider.provider_name] = existing.model_copy(
                        update={"healthy": False, "reason": error_message}
                    )

        flight_results = [
            result for result in results if isinstance(result, FlightSearchResult)
        ]
        stay_results = [result for result in results if isinstance(result, StaySearchResult)]

        car_redirect_url = None
        car_redirect_label = None
        if proposal.needs_car:
            car_redirect_url = self._build_car_redirect_url(
                destination=proposal.destination,
                travel_window=proposal.travel_window,
                travelers=request.travelers,
            )
            car_redirect_label = "Search car rentals"

        return ItineraryPriceResponse(
            proposal_id=request.proposal_id,
            flight_results=flight_results,
            stay_results=stay_results,
            car_redirect_url=car_redirect_url,
            car_redirect_label=car_redirect_label,
            provider_status=list(status_map.values()),
            warnings=warnings,
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

    def _build_itinerary_clarification_state(
        self,
        *,
        travelers: TravelerCounts,
        budget_range: ClarificationBudgetRange | None,
        candidate_destinations: list[str],
        travel_window: SearchDateRange,
        travelers_defaulted: bool,
        timeline_defaulted: bool,
    ) -> ClarificationState | None:
        destination_state = ClarificationSlotState(
            slot=ClarificationSlot.DESTINATION,
            value_label=(candidate_destinations[0] if candidate_destinations else "Anywhere"),
            confidence=1.0,
            ambiguous=False,
            source="system",
        )
        timeline_state = ClarificationSlotState(
            slot=ClarificationSlot.TIMELINE,
            value_label=travel_window.start.isoformat(),
            confidence=0.0 if timeline_defaulted else 1.0,
            ambiguous=timeline_defaulted,
            source="system",
        )
        trip_length_state = ClarificationSlotState(
            slot=ClarificationSlot.TRIP_LENGTH,
            value_label=f"{self._duration_nights(travel_window)} days",
            confidence=0.5 if travelers_defaulted else 1.0,
            ambiguous=travelers_defaulted,
            source="system",
        )
        budget_state = ClarificationSlotState(
            slot=ClarificationSlot.BUDGET,
            value_label=(
                f"{budget_range.minimum}-{budget_range.maximum}"
                if budget_range and (budget_range.minimum is not None or budget_range.maximum is not None)
                else None
            ),
            confidence=1.0 if budget_range else 0.0,
            ambiguous=budget_range is None,
            source="system",
        )

        slot_states = {
            ClarificationSlot.DESTINATION: destination_state,
            ClarificationSlot.TIMELINE: timeline_state,
            ClarificationSlot.TRIP_LENGTH: trip_length_state,
            ClarificationSlot.BUDGET: budget_state,
        }
        state = build_clarification_state(slot_states)
        if state.all_critical_slots_resolved:
            return None
        if state.next_question is None:
            state = state.model_copy(update={"next_question": SLOT_PROMPTS[ClarificationSlot.BUDGET]})
        return state

    async def _run_provider_inventory(
        self,
        provider: TravelProvider,
        request: SearchRequest,
        inventory_type: InventoryType,
    ) -> tuple[TravelProvider, InventoryType, list[SearchResult], str | None]:
        if not provider.is_configured:
            reason = provider.unconfigured_reason or "provider is not configured"
            return provider, inventory_type, [], (
                f"{provider.display_name} {inventory_type.value} search unavailable: {reason}"
            )

        try:
            results = await asyncio.wait_for(
                provider.search(request, inventory_type),
                timeout=provider.timeout_seconds,
            )
            return provider, inventory_type, results, None
        except TimeoutError:
            return provider, inventory_type, [], (
                f"{provider.display_name} {inventory_type.value} search unavailable: timed out"
            )
        except ProviderError as exc:
            return provider, inventory_type, [], (
                f"{provider.display_name} {inventory_type.value} search unavailable: {exc}"
            )

    def _build_car_redirect_url(
        self,
        *,
        destination: str,
        travel_window: SearchDateRange,
        travelers: TravelerCounts,
    ) -> str:
        params: dict[str, str | int] = {
            "destination": destination,
            "pickupDate": travel_window.start.isoformat(),
            "driversAgeOnPickup": 30,
            "adultCount": travelers.adults,
        }
        if travel_window.end:
            params["dropoffDate"] = travel_window.end.isoformat()
        return f"https://www.expedia.com/carsearch?{urlencode(params)}"


itinerary_service = ItineraryService()
