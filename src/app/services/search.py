from __future__ import annotations

import asyncio
import calendar
from collections import deque
import hashlib
import json
import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy.exc import SQLAlchemyError

from src.app.core.config import settings
from src.app.db.redis import redis_client
from src.app.models.search import ProviderRun, SearchRun
from src.app.models.user_session import SearchHistory, UserPreference
from src.app.nlp.intent import extract_budget_range, extract_intent, extract_route_hints
from src.app.providers import get_provider_registry
from src.app.providers.base import ProviderError, TravelProvider
from src.app.schemas.search import (
    AppliedFilters,
    ClarificationAnswer,
    ClarificationBudgetRange,
    ClarificationRecapEdit,
    ClarificationSlot,
    ClarificationSlotState,
    ClarificationState,
    ConstraintUpdates,
    DegradedProvider,
    DegradedState,
    FlightSearchResult,
    InventoryType,
    NoFlightGuidance,
    ProviderStatus,
    RecommendationPackage,
    SearchDateRange,
    SearchRequest,
    SearchResponse,
    SearchResult,
    StaySearchResult,
)
from src.app.services.airfare_normalization import normalize_airfare_offer
from src.app.services.clarification import (
    CRITICAL_SLOT_ORDER,
    FLIGHT_PREREQUISITE_FIELDS,
    GLOBAL_CONFIDENCE_THRESHOLD,
    build_continue_block_reason,
    build_destination_suggestions,
    build_flight_requirement_warning,
    build_clarification_state,
    get_missing_flight_prerequisites,
    make_history_entry,
    normalize_destination_candidates,
    prioritize_flight_prerequisites_for_discovery,
    reopen_related_slots,
    resolve_destination_selection_mode,
    select_next_question,
    slot_state_from_metadata,
)

logger = logging.getLogger(__name__)


@dataclass
class ProviderExecution:
    provider: TravelProvider
    inventory_type: InventoryType
    configured: bool
    cache_hit: bool
    duration_ms: int
    result_count: int
    results: list[SearchResult]
    error_message: str | None = None
    fallback_attempts: list[str] = field(default_factory=list)


class SearchService:
    def __init__(self) -> None:
        self.providers = get_provider_registry()

    async def provider_status(self) -> list[ProviderStatus]:
        statuses = await asyncio.gather(
            *[provider.healthcheck() for provider in self.providers]
        )
        return statuses

    async def search(self, request: SearchRequest, db=None) -> SearchResponse:
        resolved_request, warnings, clarification_state = self._resolve_request(request)
        search_id = str(uuid.uuid4())
        prefetch_executions: list[ProviderExecution] = []

        if (
            clarification_state
            and not clarification_state.all_critical_slots_resolved
            and self._should_block_for_clarification(clarification_state)
        ):
            prefetch_executions = await self._prefetch_flights_if_eligible(
                resolved_request,
                allow_visible_flights=False,
            )
            warnings.extend(
                self._build_execution_warnings(
                    prefetch_executions, include_empty_flight_warning=False
                )
            )
            statuses = await self.provider_status()
            statuses = self._apply_execution_status(statuses, prefetch_executions)
            return SearchResponse(
                search_id=search_id,
                query=resolved_request.query or request.query or "",
                requested_inventory=resolved_request.inventory,
                applied_filters=AppliedFilters.from_request(resolved_request),
                provider_status=statuses,
                degraded_state=self._build_degraded_state(prefetch_executions),
                warnings=self._dedupe(warnings),
                results=[],
                clarification_state=clarification_state,
                no_flight_guidance=self._build_no_flight_guidance(
                    request=resolved_request,
                    clarification_state=clarification_state,
                    executions=prefetch_executions,
                    warnings=self._dedupe(warnings),
                    results=[],
                ),
            )

        visible_inventory = list(resolved_request.inventory)
        allow_visible_flights, flight_gate_warning = self._can_show_flights(resolved_request)
        if InventoryType.FLIGHT in visible_inventory and not allow_visible_flights:
            visible_inventory = [
                inventory for inventory in visible_inventory if inventory != InventoryType.FLIGHT
            ]
            if flight_gate_warning:
                warnings.append(flight_gate_warning)

        prefetch_executions = await self._prefetch_flights_if_eligible(
            resolved_request,
            allow_visible_flights=allow_visible_flights,
        )

        tasks = []
        for provider in self.providers:
            for inventory_type in visible_inventory:
                if provider.supports_inventory(inventory_type):
                    tasks.append(
                        self._execute_provider(provider, resolved_request, inventory_type)
                    )

        executions = await asyncio.gather(*tasks)
        all_executions = [*executions, *prefetch_executions]
        statuses = await self.provider_status()
        statuses = self._apply_execution_status(statuses, all_executions)
        results: list[SearchResult] = []
        for execution in executions:
            results.extend(execution.results)
        warnings.extend(self._build_execution_warnings(executions))
        warnings.extend(
            self._build_execution_warnings(
                prefetch_executions, include_empty_flight_warning=False
            )
        )

        ranked_results = self._merge_results(results)
        ranked_results = self._normalize_flight_results(
            ranked_results,
            request=resolved_request,
        )
        recommendation_packages = self._build_recommendation_packages(
            request=resolved_request,
            results=ranked_results,
        )
        response = SearchResponse(
            search_id=search_id,
            query=resolved_request.query or "",
            requested_inventory=resolved_request.inventory,
            applied_filters=AppliedFilters.from_request(resolved_request),
            provider_status=statuses,
            degraded_state=self._build_degraded_state(all_executions),
            warnings=self._dedupe(warnings),
            results=ranked_results,
            clarification_state=clarification_state,
            no_flight_guidance=self._build_no_flight_guidance(
                request=resolved_request,
                clarification_state=clarification_state,
                executions=all_executions,
                warnings=self._dedupe(warnings),
                results=ranked_results,
            ),
            recommendation_packages=recommendation_packages,
        )
        self._cache_response(resolved_request, response)
        self._record_search(db, response, resolved_request, all_executions)
        return response

    def _resolve_request(self, request: SearchRequest) -> tuple[SearchRequest, list[str], ClarificationState]:
        warnings: list[str] = []
        request = self._merge_request_with_clarification_state(request)
        intent = extract_intent(request.query) if request.query else {}
        request = self._apply_intent_signals(request, intent)
        slot_states = self._build_slot_states(request, intent)
        history = list(request.clarification_state.history) if request.clarification_state else []

        request, slot_states, history, turn_warnings = self._apply_clarification_turn(
            request=request,
            slot_states=slot_states,
            history=history,
        )
        warnings.extend(turn_warnings)

        if slot_states[ClarificationSlot.DESTINATION].confidence < GLOBAL_CONFIDENCE_THRESHOLD:
            warnings.append("Destination is still unclear; please confirm to improve results.")

        resolved_destination_candidates = normalize_destination_candidates(
            destination_candidates=request.destination_candidates,
            destination=request.destination,
        )
        selection_mode = resolve_destination_selection_mode(
            request.destination_selection_mode,
            resolved_destination_candidates,
            request.destination,
        )
        if (
            resolved_destination_candidates != request.destination_candidates
            or selection_mode != request.destination_selection_mode
        ):
            request = request.model_copy(
                update={
                    "destination_candidates": resolved_destination_candidates,
                    "destination_selection_mode": selection_mode,
                }
            )

        flight_requirements_pending = (
            get_missing_flight_prerequisites(request)
            if InventoryType.FLIGHT in request.inventory
            else []
        )
        prioritize_flight_prerequisites_for_discovery(
            slot_states=slot_states,
            flight_requirements_pending=flight_requirements_pending,
        )

        clarification_state = build_clarification_state(
            slot_states,
            history=history,
            weather_state=slot_states.get(ClarificationSlot.WEATHER),
            resolved_origin=request.origin,
            resolved_date_range=request.date_range,
            flight_requirements_pending=flight_requirements_pending,
            continue_block_reason=build_continue_block_reason(flight_requirements_pending),
        )
        clarification_state = self._apply_repeated_question_guard(
            clarification_state=clarification_state,
            slot_states=slot_states,
            previous_state=request.clarification_state,
        )
        clarification_state = clarification_state.model_copy(
            update={
                "destination_suggestions": build_destination_suggestions(
                    destination_state=slot_states[ClarificationSlot.DESTINATION],
                    query_text=request.query,
                    selected_candidates=resolved_destination_candidates,
                ),
                "supports_multi_destination_compare": True,
                "destination_selection_mode": selection_mode,
                "resolved_destination_candidates": resolved_destination_candidates,
            }
        )
        return request.model_copy(update={"clarification_state": clarification_state}), warnings, clarification_state

    def _build_no_flight_guidance(
        self,
        *,
        request: SearchRequest,
        clarification_state: ClarificationState | None,
        executions: list[ProviderExecution],
        warnings: list[str],
        results: list[SearchResult],
    ) -> NoFlightGuidance | None:
        if InventoryType.FLIGHT not in request.inventory:
            return None
        has_flights = any(isinstance(result, FlightSearchResult) for result in results)
        if has_flights:
            return None

        pending_requirements = clarification_state.flight_requirements_pending if clarification_state else []
        if pending_requirements:
            first_requirement = pending_requirements[0]
            follow_up_prompt = (
                "What airport or city are you flying from?"
                if first_requirement == "origin"
                else "What travel dates should I use? You can reply YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD."
            )
            return NoFlightGuidance(
                code="missing_prerequisites",
                explanation=(
                    "Flight prerequisites are still missing, so live airfare provenance "
                    "and freshness details are not available yet."
                ),
                actions=[
                    f"Add the missing prerequisites: {', '.join(pending_requirements)}.",
                    "Continue after updating those details to fetch live airfare offers.",
                ],
                follow_up_prompt=follow_up_prompt,
            )

        flight_executions = [
            execution
            for execution in executions
            if execution.inventory_type == InventoryType.FLIGHT
        ]
        has_execution_error = any(execution.error_message for execution in flight_executions)
        configured_flight_empty = any(
            execution.configured and not execution.error_message and execution.result_count == 0
            for execution in flight_executions
        )
        fallback_attempts: list[str] = []
        for execution in flight_executions:
            for attempt in execution.fallback_attempts:
                if attempt not in fallback_attempts:
                    fallback_attempts.append(attempt)

        if has_execution_error:
            return NoFlightGuidance(
                code="provider_unavailable",
                explanation=(
                    "One or more flight providers are currently unavailable, so airfare "
                    "provenance and freshness details cannot be shown right now."
                ),
                actions=[
                    "Retry this search in a few minutes.",
                    "Use stay recommendations now and rerun flight search after provider recovery.",
                ],
                follow_up_prompt="Share alternate dates or nearby airports and I can retry airfare search.",
            )

        if configured_flight_empty:
            return NoFlightGuidance(
                code="no_offers",
                explanation=(
                    "Providers returned no airfare offers for this route/date combination, "
                    "so provenance and freshness metadata are unavailable for this search."
                ),
                actions=[
                    "Try nearby airports or wider date ranges.",
                    "Relax nonstop, time, or budget filters and search again.",
                ],
                fallback_attempts=fallback_attempts,
                follow_up_prompt="Tell me nearby airports or alternate dates and I will retry now.",
            )

        return NoFlightGuidance(
            code="general_no_results",
            explanation=(
                "No live airfare results are currently available for this request, so "
                "provenance and freshness details cannot be displayed yet."
            ),
            actions=[
                "Broaden travel constraints and retry the search.",
                "Confirm at least one live flight provider is configured.",
            ],
            follow_up_prompt="Tell me what to loosen first: dates, airports, or nonstop preference.",
        )

    def _apply_intent_signals(self, request: SearchRequest, intent: dict) -> SearchRequest:
        if not request.query:
            return request

        updates: dict = {}
        if not request.destination and intent.get("location"):
            updates["destination"] = intent["location"]

        if not request.origin:
            origin_hint = intent.get("origin_hint")
            if isinstance(origin_hint, str) and origin_hint.strip():
                updates["origin"] = origin_hint.strip()
            else:
                extracted_origin = self._extract_origin_hint(request.query)
                if extracted_origin:
                    updates["origin"] = extracted_origin

        if not request.date_range:
            parsed_date_range = None
            if intent.get("date_range"):
                parsed_date_range = self._parse_date_range(intent["date_range"])
            if not parsed_date_range:
                normalized_timeline = intent.get("normalized_timeline")
                if isinstance(normalized_timeline, dict):
                    window = normalized_timeline.get("window") or {}
                    parsed_date_range = self._parse_timeline_window(
                        window.get("start"),
                        window.get("end"),
                    )
            if parsed_date_range:
                updates["date_range"] = parsed_date_range

        if intent.get("travelers"):
            updates["travelers"] = intent["travelers"]

        duration_days = intent.get("duration_days")
        effective_date_range = updates.get("date_range") or request.date_range
        if duration_days and effective_date_range:
            adjusted_end = (
                effective_date_range.start + timedelta(days=duration_days)
            )
            updates["date_range"] = SearchDateRange(
                start=effective_date_range.start,
                end=adjusted_end
            )

        if not updates:
            return request
        return request.model_copy(update=updates)

    def _should_block_for_clarification(self, clarification_state: ClarificationState) -> bool:
        destination = clarification_state.destination
        return destination.ambiguous or destination.confidence < GLOBAL_CONFIDENCE_THRESHOLD

    def _build_slot_states(
        self, request: SearchRequest, intent: dict
    ) -> dict[ClarificationSlot, ClarificationSlotState]:
        slot_metadata = intent.get("slot_metadata", {})
        normalized_timeline = intent.get("normalized_timeline")
        normalized_budget = intent.get("normalized_budget")
        normalized_weather = intent.get("normalized_weather")

        destination_state = slot_state_from_metadata(
            ClarificationSlot.DESTINATION,
            {
                "value": request.destination,
                "confidence": 1.0 if request.destination else 0.0,
                "ambiguous": request.destination is None,
                "source_text": request.destination,
            }
            if request.destination
            else (
                slot_metadata.get("destination")
                or {
                    "value": None,
                    "confidence": 0.0,
                    "ambiguous": True,
                    "source_text": None,
                }
            ),
        )
        timeline_source = None
        if request.date_range:
            timeline_source = {
                "window": {
                    "start": request.date_range.start.isoformat(),
                    "end": request.date_range.end.isoformat() if request.date_range.end else None,
                },
                "precision": "explicit",
                "source_text": request.date_range.start.isoformat(),
            }
        timeline_state = slot_state_from_metadata(
            ClarificationSlot.TIMELINE,
            {
                "value": timeline_source or normalized_timeline,
                "confidence": 1.0 if (request.date_range or normalized_timeline) else 0.0,
                "ambiguous": request.date_range is None and normalized_timeline is None,
                "source_text": request.date_range.start.isoformat() if request.date_range else None,
            }
            if request.date_range
            else (
                slot_metadata.get("timeline")
                or {
                    "value": normalized_timeline,
                    "confidence": 0.0 if normalized_timeline is None else 0.7,
                    "ambiguous": normalized_timeline is None,
                    "source_text": None,
                }
            ),
        )
        trip_length_state = slot_state_from_metadata(
            ClarificationSlot.TRIP_LENGTH,
            {
                "value": request.trip_length_days,
                "confidence": 1.0 if request.trip_length_days else 0.0,
                "ambiguous": request.trip_length_days is None,
                "source_text": str(request.trip_length_days) if request.trip_length_days else None,
            }
            if request.trip_length_days
            else (
                slot_metadata.get("trip_length")
                or {
                    "value": None,
                    "confidence": 0.0,
                    "ambiguous": True,
                    "source_text": None,
                }
            ),
        )
        budget_state = slot_state_from_metadata(
            ClarificationSlot.BUDGET,
            {
                "value": (
                    request.budget_range.model_dump(mode="json")
                    if request.budget_range
                    else normalized_budget
                ),
                "confidence": 1.0 if (request.budget_range or normalized_budget) else 0.0,
                "ambiguous": request.budget_range is None and normalized_budget is None,
                "source_text": request.budget_range.model_dump_json() if request.budget_range else None,
            }
            if request.budget_range
            else (
                slot_metadata.get("budget")
                or {
                    "value": normalized_budget,
                    "confidence": 0.0 if normalized_budget is None else 0.8,
                    "ambiguous": normalized_budget is None,
                    "source_text": None,
                }
            ),
        )
        weather_state = slot_state_from_metadata(
            ClarificationSlot.WEATHER,
            {
                "value": (
                    request.weather_preference.model_dump(mode="json")
                    if request.weather_preference
                    else normalized_weather
                ),
                "confidence": 1.0 if (request.weather_preference or normalized_weather) else 0.0,
                "ambiguous": request.weather_preference is None and normalized_weather is None,
                "source_text": request.weather_preference.source_text if request.weather_preference else None,
            }
            if request.weather_preference
            else (
                slot_metadata.get("weather")
                or {
                    "value": normalized_weather,
                    "confidence": 0.0 if normalized_weather is None else 0.8,
                    "ambiguous": normalized_weather is None,
                    "source_text": None,
                }
            ),
        )

        return {
            ClarificationSlot.DESTINATION: destination_state,
            ClarificationSlot.TIMELINE: timeline_state,
            ClarificationSlot.TRIP_LENGTH: trip_length_state,
            ClarificationSlot.BUDGET: budget_state,
            ClarificationSlot.WEATHER: weather_state,
        }

    def _apply_clarification_turn(
        self,
        *,
        request: SearchRequest,
        slot_states: dict[ClarificationSlot, ClarificationSlotState],
        history: list,
    ) -> tuple[SearchRequest, dict[ClarificationSlot, ClarificationSlotState], list, list[str]]:
        warnings: list[str] = []
        updates: dict = {}
        allowed_update_slots = {
            ClarificationSlot.DESTINATION,
            ClarificationSlot.TIMELINE,
            ClarificationSlot.TRIP_LENGTH,
            ClarificationSlot.BUDGET,
            ClarificationSlot.WEATHER,
        }

        if request.query and not request.destination:
            intent = extract_intent(request.query)
            if intent.get("location"):
                updates["destination"] = intent["location"]

            if not request.date_range and intent.get("date_range"):
                parsed_date_range = self._parse_date_range(intent["date_range"])
                if parsed_date_range:
                    updates["date_range"] = parsed_date_range

        clarification_answer = request.clarification_answer
        if isinstance(clarification_answer, dict):
            clarification_answer = ClarificationAnswer.model_validate(clarification_answer)

        if clarification_answer:
            slot = clarification_answer.slot
            if slot in allowed_update_slots:
                previous_value = slot_states[slot].value_label
                if clarification_answer.explicit_unknown:
                    slot_states[slot] = slot_states[slot].model_copy(
                        update={
                            "explicit_unknown": True,
                            "ambiguous": False,
                            "confidence": 1.0,
                            "value_label": "I don't know",
                            "source": "user",
                        }
                    )
                    warnings.append(f"{slot.value.replace('_', ' ').title()} marked as unknown; proceeding with broader options.")
                    history.append(
                        make_history_entry(
                            slot=slot,
                            previous_value=previous_value,
                            new_value="I don't know",
                            action="unknown",
                        )
                    )
                else:
                    answer_text = (clarification_answer.answer_text or "").strip()
                    self._apply_slot_answer(slot, answer_text, updates, slot_states)
                    history.append(
                        make_history_entry(
                            slot=slot,
                            previous_value=previous_value,
                            new_value=answer_text,
                            action="answer",
                        )
                    )

        recap_edit = request.recap_edit
        if isinstance(recap_edit, dict):
            recap_edit = ClarificationRecapEdit.model_validate(recap_edit)

        if recap_edit:
            slot = recap_edit.slot
            if slot in allowed_update_slots:
                previous_value = slot_states[slot].value_label
                if recap_edit.explicit_unknown:
                    slot_states[slot] = slot_states[slot].model_copy(
                        update={
                            "explicit_unknown": True,
                            "ambiguous": False,
                            "confidence": 1.0,
                            "value_label": "I don't know",
                            "source": "user",
                        }
                    )
                    history.append(
                        make_history_entry(
                            slot=slot,
                            previous_value=previous_value,
                            new_value="I don't know",
                            action="unknown",
                        )
                    )
                else:
                    edited_value = (recap_edit.edited_value or "").strip()
                    self._apply_slot_answer(slot, edited_value, updates, slot_states)
                    history.append(
                        make_history_entry(
                            slot=slot,
                            previous_value=previous_value,
                            new_value=edited_value,
                            action="recap_edit",
                        )
                    )
                reopen_related_slots(slot_states, slot)

        constraint_updates = request.constraint_updates
        if isinstance(constraint_updates, dict):
            constraint_updates = ConstraintUpdates.model_validate(constraint_updates)

        if constraint_updates:
            self._apply_constraint_updates(
                updates=updates,
                constraint_updates=constraint_updates,
                slot_states=slot_states,
                history=history,
                allowed_update_slots=allowed_update_slots,
            )

        if updates:
            request = request.model_copy(update=updates)
        return request, slot_states, history, warnings

    def _merge_request_with_clarification_state(self, request: SearchRequest) -> SearchRequest:
        state = request.clarification_state
        if not state:
            return request

        updates: dict = {}
        if not request.origin and state.resolved_origin:
            updates["origin"] = state.resolved_origin
        if not request.destination and state.destination.value_label:
            updates["destination"] = state.destination.value_label
        if not request.trip_length_days and state.trip_length.value_label:
            trip_length = self._parse_trip_length_answer(state.trip_length.value_label)
            if trip_length:
                updates["trip_length_days"] = trip_length
        if not request.date_range and state.resolved_date_range:
            updates["date_range"] = state.resolved_date_range
        elif not request.date_range and state.timeline.value_label:
            parsed_range = self._parse_timeline_answer(state.timeline.value_label)
            if parsed_range:
                updates["date_range"] = parsed_range
        if not request.budget_range and state.budget.value_label:
            budget = self._parse_budget_answer(state.budget.value_label)
            if budget:
                updates["budget_range"] = budget

        if not updates:
            return request
        return request.model_copy(update=updates)

    def _apply_repeated_question_guard(
        self,
        *,
        clarification_state: ClarificationState,
        slot_states: dict[ClarificationSlot, ClarificationSlotState],
        previous_state: ClarificationState | None,
    ) -> ClarificationState:
        next_question = clarification_state.next_question
        if not next_question or not previous_state or not previous_state.next_question:
            return clarification_state

        if previous_state.next_question.slot != next_question.slot:
            return clarification_state.model_copy(
                update={
                    "loop_guard_counter": 0,
                    "repeated_question_slot": None,
                }
            )

        repeated_count = (previous_state.loop_guard_counter or 0) + 1
        repeated_slot = next_question.slot
        updated_state = clarification_state.model_copy(
            update={
                "loop_guard_counter": repeated_count,
                "repeated_question_slot": repeated_slot,
            }
        )
        if repeated_count < 2:
            return updated_state

        # If we already asked this slot repeatedly and it now has value, advance.
        state_for_slot = slot_states[repeated_slot]
        if state_for_slot.value_label or state_for_slot.explicit_unknown:
            candidate_states = {
                slot: state
                for slot, state in slot_states.items()
                if slot != repeated_slot
            }
            fallback_question = select_next_question(
                {
                    **candidate_states,
                    repeated_slot: state_for_slot.model_copy(
                        update={
                            "ambiguous": False,
                            "confidence": 1.0,
                        }
                    ),
                }
            )
            return updated_state.model_copy(
                update={
                    "next_question": fallback_question,
                }
            )
        return updated_state

    def _apply_slot_answer(
        self,
        slot: ClarificationSlot,
        answer_text: str,
        updates: dict,
        slot_states: dict[ClarificationSlot, ClarificationSlotState],
    ) -> None:
        if slot == ClarificationSlot.DESTINATION:
            updates["destination"] = answer_text
        elif slot == ClarificationSlot.TIMELINE:
            parsed = self._parse_timeline_answer(answer_text)
            if parsed:
                updates["date_range"] = parsed
        elif slot == ClarificationSlot.TRIP_LENGTH:
            value = self._parse_trip_length_answer(answer_text)
            if value:
                updates["trip_length_days"] = value
        elif slot == ClarificationSlot.BUDGET:
            parsed_budget = self._parse_budget_answer(answer_text)
            if parsed_budget:
                updates["budget_range"] = parsed_budget
        elif slot == ClarificationSlot.WEATHER:
            weather = self._parse_weather_answer(answer_text)
            if weather:
                updates["weather_preference"] = weather

        slot_states[slot] = slot_states[slot].model_copy(
            update={
                "value_label": answer_text,
                "confidence": 1.0,
                "ambiguous": False,
                "explicit_unknown": False,
                "source_text": answer_text,
                "source": "user",
            }
        )

    def _apply_constraint_updates(
        self,
        *,
        updates: dict,
        constraint_updates: ConstraintUpdates,
        slot_states: dict[ClarificationSlot, ClarificationSlotState],
        history: list,
        allowed_update_slots: set[ClarificationSlot],
    ) -> None:
        if constraint_updates.origin is not None:
            updates["origin"] = constraint_updates.origin

        if constraint_updates.destination is not None:
            previous = slot_states[ClarificationSlot.DESTINATION].value_label
            updates["destination"] = constraint_updates.destination
            slot_states[ClarificationSlot.DESTINATION] = slot_states[ClarificationSlot.DESTINATION].model_copy(
                update={
                    "value_label": constraint_updates.destination,
                    "confidence": 1.0,
                    "ambiguous": False,
                    "source": "user",
                    "source_text": constraint_updates.destination,
                }
            )
            history.append(
                make_history_entry(
                    slot=ClarificationSlot.DESTINATION,
                    previous_value=previous,
                    new_value=constraint_updates.destination,
                    action="constraint_update",
                )
            )
        if constraint_updates.destination_candidates:
            updates["destination_candidates"] = normalize_destination_candidates(
                destination_candidates=constraint_updates.destination_candidates,
                destination=updates.get("destination"),
            )
        if constraint_updates.destination_selection_mode is not None:
            updates["destination_selection_mode"] = constraint_updates.destination_selection_mode
        if constraint_updates.date_range is not None:
            previous = slot_states[ClarificationSlot.TIMELINE].value_label
            updates["date_range"] = constraint_updates.date_range
            slot_states[ClarificationSlot.TIMELINE] = slot_states[ClarificationSlot.TIMELINE].model_copy(
                update={
                    "value_label": constraint_updates.date_range.start.isoformat(),
                    "normalized_value": constraint_updates.date_range.model_dump(mode="json"),
                    "confidence": 1.0,
                    "ambiguous": False,
                    "source": "user",
                    "source_text": constraint_updates.date_range.start.isoformat(),
                }
            )
            history.append(
                make_history_entry(
                    slot=ClarificationSlot.TIMELINE,
                    previous_value=previous,
                    new_value=constraint_updates.date_range.start.isoformat(),
                    action="constraint_update",
                )
            )
        if constraint_updates.trip_length_days is not None:
            previous = slot_states[ClarificationSlot.TRIP_LENGTH].value_label
            updates["trip_length_days"] = constraint_updates.trip_length_days
            slot_states[ClarificationSlot.TRIP_LENGTH] = slot_states[ClarificationSlot.TRIP_LENGTH].model_copy(
                update={
                    "value_label": f"{constraint_updates.trip_length_days} days",
                    "confidence": 1.0,
                    "ambiguous": False,
                    "source": "user",
                    "source_text": str(constraint_updates.trip_length_days),
                }
            )
            history.append(
                make_history_entry(
                    slot=ClarificationSlot.TRIP_LENGTH,
                    previous_value=previous,
                    new_value=str(constraint_updates.trip_length_days),
                    action="constraint_update",
                )
            )
        if constraint_updates.budget_range is not None:
            previous = slot_states[ClarificationSlot.BUDGET].value_label
            updates["budget_range"] = constraint_updates.budget_range
            slot_states[ClarificationSlot.BUDGET] = slot_states[ClarificationSlot.BUDGET].model_copy(
                update={
                    "value_label": f"{constraint_updates.budget_range.minimum}-{constraint_updates.budget_range.maximum}",
                    "normalized_value": constraint_updates.budget_range.model_dump(mode="json"),
                    "confidence": 1.0,
                    "ambiguous": False,
                    "source": "user",
                    "source_text": f"{constraint_updates.budget_range.minimum}-{constraint_updates.budget_range.maximum}",
                }
            )
            history.append(
                make_history_entry(
                    slot=ClarificationSlot.BUDGET,
                    previous_value=previous,
                    new_value=f"{constraint_updates.budget_range.minimum}-{constraint_updates.budget_range.maximum}",
                    action="constraint_update",
                )
            )
        if constraint_updates.date_flexibility is not None:
            updates["date_flexibility"] = constraint_updates.date_flexibility
        if constraint_updates.flight_preferences is not None:
            updates["flight_preferences"] = constraint_updates.flight_preferences
        if constraint_updates.trip_style_tags:
            updates["trip_style_tags"] = [
                tag.strip() for tag in constraint_updates.trip_style_tags if tag.strip()
            ]
        if constraint_updates.weather_preference is not None:
            previous = slot_states[ClarificationSlot.WEATHER].value_label
            updates["weather_preference"] = constraint_updates.weather_preference
            slot_states[ClarificationSlot.WEATHER] = slot_states[ClarificationSlot.WEATHER].model_copy(
                update={
                    "value_label": constraint_updates.weather_preference.source_text or "weather preference",
                    "normalized_value": constraint_updates.weather_preference.model_dump(mode="json"),
                    "confidence": 1.0,
                    "ambiguous": False,
                    "source": "user",
                    "source_text": constraint_updates.weather_preference.source_text,
                }
            )
            history.append(
                make_history_entry(
                    slot=ClarificationSlot.WEATHER,
                    previous_value=previous,
                    new_value=constraint_updates.weather_preference.source_text,
                    action="constraint_update",
                )
            )

        for slot in constraint_updates.explicit_unknown_slots:
            if slot not in allowed_update_slots:
                continue
            previous = slot_states[slot].value_label
            slot_states[slot] = slot_states[slot].model_copy(
                update={
                    "explicit_unknown": True,
                    "ambiguous": False,
                    "confidence": 1.0,
                    "value_label": "I don't know",
                    "source": "user",
                }
            )
            history.append(
                make_history_entry(
                    slot=slot,
                    previous_value=previous,
                    new_value="I don't know",
                    action="unknown",
                )
            )

    def _parse_trip_length_answer(self, answer_text: str) -> int | None:
        lowered = answer_text.lower()
        match = next((token for token in answer_text.split() if token.isdigit()), None)
        if match:
            return int(match)
        word_numbers = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
            "eleven": 11,
            "twelve": 12,
            "fortnight": 14,
        }
        for word, value in word_numbers.items():
            if f"{word} day" in lowered:
                return value
        if "weekend" in lowered:
            return 2
        if "week" in lowered:
            return 7
        return None

    def _parse_timeline_answer(self, answer_text: str) -> SearchDateRange | None:
        parsed = self._parse_date_range({"start": answer_text, "end": None})
        if parsed:
            return parsed

        iso_range_match = re.search(
            r"(\d{4}-\d{2}-\d{2})\s*(?:to|through|until|-)\s*(\d{4}-\d{2}-\d{2})",
            answer_text,
            re.IGNORECASE,
        )
        if iso_range_match:
            parsed = self._parse_date_range(
                {"start": iso_range_match.group(1), "end": iso_range_match.group(2)}
            )
            if parsed:
                return parsed

        answer_intent = extract_intent(answer_text)
        normalized_timeline = answer_intent.get("normalized_timeline")
        if isinstance(normalized_timeline, dict):
            window = normalized_timeline.get("window") or {}
            start = window.get("start")
            end = window.get("end")
            parsed = self._parse_timeline_window(start, end)
            if parsed:
                return parsed
        return None

    def _parse_timeline_window(self, start: str | None, end: str | None) -> SearchDateRange | None:
        start_date = self._parse_date_value(start)
        end_date = self._parse_date_value(end)
        if start_date:
            return SearchDateRange(start=start_date, end=end_date)

        if not start:
            return None

        lowered = str(start).strip().lower()
        month_start = self._month_start(lowered)
        if month_start:
            month_end = self._month_end(month_start.year, month_start.month)
            return SearchDateRange(start=month_start, end=month_end)

        season_range = self._season_range(lowered)
        if season_range:
            return SearchDateRange(start=season_range[0], end=season_range[1])

        if lowered == "next month":
            return self._next_month_range()
        return None

    def _month_start(self, token: str) -> date | None:
        months = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }
        month = months.get(token)
        if not month:
            return None
        today = date.today()
        year = today.year
        if month < today.month:
            year += 1
        return date(year, month, 1)

    def _month_end(self, year: int, month: int) -> date:
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, last_day)

    def _next_month_range(self) -> SearchDateRange:
        today = date.today()
        month = today.month + 1
        year = today.year
        if month == 13:
            month = 1
            year += 1
        start = date(year, month, 1)
        end = self._month_end(year, month)
        return SearchDateRange(start=start, end=end)

    def _season_range(self, token: str) -> tuple[date, date] | None:
        year = date.today().year
        if token == "summer":
            return date(year, 6, 1), date(year, 8, 31)
        if token == "spring":
            return date(year, 3, 1), date(year, 5, 31)
        if token == "fall":
            return date(year, 9, 1), date(year, 11, 30)
        if token == "winter":
            return date(year, 12, 1), date(year + 1, 2, 28)
        if token == "early summer":
            return date(year, 6, 1), date(year, 7, 15)
        return None

    def _parse_budget_answer(self, answer_text: str):
        from src.app.schemas.search import ClarificationBudgetRange
        parsed_range = extract_budget_range(answer_text)
        if parsed_range:
            return parsed_range

        lowered = answer_text.lower()
        qualitative_ranges = {
            "budget": (0, 1500),
            "cheap": (0, 1500),
            "affordable": (0, 1500),
            "moderate": (1500, 3500),
            "mid-range": (1500, 3500),
            "midrange": (1500, 3500),
            "luxury": (3500, 10000),
            "luxurious": (3500, 10000),
        }
        for term, (minimum, maximum) in qualitative_ranges.items():
            if term in lowered:
                return ClarificationBudgetRange(
                    minimum=float(minimum), maximum=float(maximum)
                )

        numbers = [
            int(item.replace(",", ""))
            for item in re.findall(r"\d[\d,]*", answer_text)
        ]
        if not numbers:
            return None
        if len(numbers) == 1:
            return ClarificationBudgetRange(minimum=0, maximum=float(numbers[0]))
        low, high = min(numbers[0], numbers[1]), max(numbers[0], numbers[1])
        return ClarificationBudgetRange(minimum=float(low), maximum=float(high))

    def _parse_weather_answer(self, answer_text: str):
        from src.app.schemas.search import WeatherPreference
        lowered = answer_text.lower()
        temperature = None
        precipitation = None
        if "warm" in lowered:
            temperature = "warm"
        elif "cool" in lowered:
            temperature = "cool"
        elif "nice" in lowered or "pleasant" in lowered:
            temperature = "pleasant"
        if "avoid rain" in lowered or "no rain" in lowered:
            precipitation = "avoid_rain"
        elif "rain" in lowered:
            precipitation = "rain_ok"
        if not temperature and not precipitation:
            return None
        return WeatherPreference(
            temperature=temperature,
            precipitation=precipitation,
            source_text=answer_text,
        )

    def _extract_origin_hint(self, query: str) -> str | None:
        route_hints = extract_route_hints(query)
        if route_hints.get("origin"):
            return route_hints["origin"]

        lowered = query.lower()
        if "from " not in lowered:
            return None
        fragment = query[lowered.index("from ") + 5 :]
        lowered_fragment = fragment.lower()
        cut_at = len(fragment)
        for separator in (
            " to ",
            " on ",
            " leaving ",
            " for ",
            " with ",
            " in ",
            " around ",
            " during ",
            " next ",
            " this ",
            " maybe ",
            " sometime ",
        ):
            index = lowered_fragment.find(separator)
            if index != -1:
                cut_at = min(cut_at, index)
        origin = fragment[:cut_at].strip(" ,.")
        if not origin:
            return None
        if len(origin) == 3 and origin.isalpha():
            return origin.upper()
        return " ".join(token.capitalize() for token in origin.split())

    async def _execute_provider(
        self, provider: TravelProvider, request: SearchRequest, inventory_type: InventoryType
    ) -> ProviderExecution:
        start = time.perf_counter()
        if not provider.is_configured:
            return ProviderExecution(
                provider=provider,
                inventory_type=inventory_type,
                configured=False,
                cache_hit=False,
                duration_ms=0,
                result_count=0,
                results=[],
                error_message=provider.unconfigured_reason,
            )

        cached = self._read_cached_provider_results(provider, request, inventory_type)
        if cached is not None:
            return ProviderExecution(
                provider=provider,
                inventory_type=inventory_type,
                configured=True,
                cache_hit=True,
                duration_ms=int((time.perf_counter() - start) * 1000),
                result_count=len(cached),
                results=cached,
            )

        try:
            deadline_seconds = self._provider_deadline_seconds(provider, inventory_type)
            results = await asyncio.wait_for(
                provider.search(request, inventory_type),
                timeout=deadline_seconds,
            )
            fallback_attempts: list[str] = []
            if (
                inventory_type == InventoryType.FLIGHT
                and provider.provider_name == "duffel"
                and not results
            ):
                fallback_attempts = ["primary_query"]
                for label, fallback_request in self._duffel_fallback_requests(request):
                    fallback_attempts.append(label)
                    fallback_results = await asyncio.wait_for(
                        provider.search(fallback_request, inventory_type),
                        timeout=deadline_seconds,
                    )
                    if fallback_results:
                        results = fallback_results
                        request = fallback_request
                        break
            self._cache_provider_results(provider, request, inventory_type, results)
            return ProviderExecution(
                provider=provider,
                inventory_type=inventory_type,
                configured=True,
                cache_hit=False,
                duration_ms=int((time.perf_counter() - start) * 1000),
                result_count=len(results),
                results=results,
                fallback_attempts=fallback_attempts,
            )
        except TimeoutError:
            return ProviderExecution(
                provider=provider,
                inventory_type=inventory_type,
                configured=True,
                cache_hit=False,
                duration_ms=int((time.perf_counter() - start) * 1000),
                result_count=0,
                results=[],
                error_message=f"timed out after {self._provider_deadline_seconds(provider, inventory_type):.1f}s deadline",
            )
        except ProviderError as exc:
            logger.warning("Provider search failed: %s", exc)
            return ProviderExecution(
                provider=provider,
                inventory_type=inventory_type,
                configured=True,
                cache_hit=False,
                duration_ms=int((time.perf_counter() - start) * 1000),
                result_count=0,
                results=[],
                error_message=str(exc),
            )

    def _duffel_fallback_requests(self, request: SearchRequest) -> list[tuple[str, SearchRequest]]:
        fallbacks: list[tuple[str, SearchRequest]] = []
        if request.flight_filters.nonstop:
            fallbacks.append(
                (
                    "relax_nonstop_filter",
                    request.model_copy(
                        update={
                            "flight_filters": request.flight_filters.model_copy(
                                update={"nonstop": False}
                            )
                        }
                    ),
                )
            )
        if request.date_range and request.date_range.start:
            widened_start = request.date_range.start - timedelta(days=2)
            widened_end = (
                request.date_range.end + timedelta(days=2)
                if request.date_range.end
                else request.date_range.start + timedelta(days=2)
            )
            fallbacks.append(
                (
                    "widen_date_window",
                    request.model_copy(
                        update={
                            "date_range": request.date_range.model_copy(
                                update={"start": widened_start, "end": widened_end}
                            )
                        }
                    ),
                )
            )
        return fallbacks

    def _provider_deadline_seconds(
        self, provider: TravelProvider, inventory_type: InventoryType
    ) -> float:
        if (
            provider.provider_name == "amadeus"
            and inventory_type == InventoryType.FLIGHT
        ):
            return max(0.1, settings.AMADEUS_REQUEST_DEADLINE_SECONDS)
        return max(0.1, provider.timeout_seconds)

    async def _prefetch_flights_if_eligible(
        self, request: SearchRequest, *, allow_visible_flights: bool
    ) -> list[ProviderExecution]:
        if allow_visible_flights:
            return []
        if not self._flight_prefetch_eligible(request):
            return []
        tasks = [
            self._execute_provider(provider, request, InventoryType.FLIGHT)
            for provider in self.providers
            if provider.supports_inventory(InventoryType.FLIGHT)
        ]
        if not tasks:
            return []
        return await asyncio.gather(*tasks)

    def _flight_prefetch_eligible(self, request: SearchRequest) -> bool:
        return bool(
            InventoryType.FLIGHT in request.inventory
            and request.destination
            and request.date_range
            and request.date_range.start
        )

    def _can_show_flights(self, request: SearchRequest) -> tuple[bool, str | None]:
        if InventoryType.FLIGHT not in request.inventory:
            return False, None
        missing_requirements = get_missing_flight_prerequisites(request)
        if missing_requirements:
            return False, build_flight_requirement_warning(missing_requirements)
        if not self._is_stable_clarification_turn(request):
            return False, "Flight results will appear after clarification updates are confirmed."
        return True, None

    def _is_stable_clarification_turn(self, request: SearchRequest) -> bool:
        return (
            request.clarification_answer is None
            and request.recap_edit is None
            and request.constraint_updates is None
        )

    def _build_execution_warnings(
        self,
        executions: list[ProviderExecution],
        *,
        include_empty_flight_warning: bool = True,
    ) -> list[str]:
        warnings: list[str] = []
        for execution in executions:
            if execution.error_message:
                warnings.append(
                    f"{execution.provider.display_name} {execution.inventory_type.value} search unavailable: {execution.error_message}"
                )
            elif (
                include_empty_flight_warning
                and execution.inventory_type == InventoryType.FLIGHT
                and execution.configured
                and execution.result_count == 0
            ):
                warnings.append(
                    f"{execution.provider.display_name} returned no flight offers for the selected route and dates."
                )
        return warnings

    def _build_degraded_state(self, executions: list[ProviderExecution]) -> DegradedState:
        degraded_by_provider: dict[str, DegradedProvider] = {}
        inventory_types: list[InventoryType] = []
        for execution in executions:
            if not execution.error_message:
                continue
            if execution.inventory_type not in inventory_types:
                inventory_types.append(execution.inventory_type)
            provider_key = execution.provider.provider_name
            existing = degraded_by_provider.get(provider_key)
            provider_inventory = (
                list(existing.inventory_types)
                if existing
                else []
            )
            if execution.inventory_type not in provider_inventory:
                provider_inventory.append(execution.inventory_type)
            degraded_by_provider[provider_key] = DegradedProvider(
                provider=provider_key,
                label=execution.provider.display_name,
                reason=execution.error_message,
                inventory_types=provider_inventory,
            )
        degraded_providers = sorted(
            degraded_by_provider.values(),
            key=lambda provider: provider.provider,
        )
        return DegradedState(
            active=bool(degraded_providers),
            inventory_types=inventory_types,
            degraded_providers=degraded_providers,
        )

    def _apply_execution_status(
        self, statuses: list[ProviderStatus], executions: list[ProviderExecution]
    ) -> list[ProviderStatus]:
        if not executions:
            return statuses

        status_map = {status.provider: status for status in statuses}
        for execution in executions:
            current = status_map.get(execution.provider.provider_name)
            if current is None:
                continue
            if execution.error_message:
                status_map[current.provider] = current.model_copy(
                    update={
                        "healthy": False,
                        "reason": execution.error_message,
                    }
                )
            elif not execution.configured:
                status_map[current.provider] = current.model_copy(
                    update={
                        "healthy": False,
                        "reason": execution.error_message or execution.provider.unconfigured_reason,
                    }
                )
        return [status_map[status.provider] for status in statuses]

    def _rank_results(self, results: list[SearchResult]) -> list[SearchResult]:
        def sort_key(item: SearchResult) -> tuple[float, float]:
            penalty = 0.0
            if isinstance(item, FlightSearchResult):
                penalty = item.stops * 10
            return (-item.score, item.total_price + penalty)

        return sorted(results, key=sort_key)

    def _merge_results(self, results: list[SearchResult]) -> list[SearchResult]:
        flight_results = [
            result for result in results if isinstance(result, FlightSearchResult)
        ]
        other_results = [
            result for result in results if not isinstance(result, FlightSearchResult)
        ]
        merged_flights = self._deterministic_flight_interleave(flight_results)
        return [*merged_flights, *self._rank_results(other_results)]

    def _normalize_flight_results(
        self, results: list[SearchResult], request: SearchRequest
    ) -> list[SearchResult]:
        fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        normalized_results: list[SearchResult] = []
        for result in results:
            if not isinstance(result, FlightSearchResult):
                normalized_results.append(result)
                continue

            normalization = normalize_airfare_offer(
                provider=result.provider,
                provider_offer_id=result.provider_offer_id,
                origin_code=result.origin_code,
                destination_code=result.destination_code,
                departure_at=result.departure_at,
                arrival_at=result.arrival_at,
                total_price=result.total_price,
                provider_currency=result.currency,
                requested_currency=request.currency_code,
                duration=result.duration,
                stops=result.stops,
                fetched_at=fetched_at,
                source_payload_ref=result.provider_offer_id,
            )
            normalized_payload = result.model_dump(mode="json")
            normalized_payload.update(normalization)
            normalized_results.append(FlightSearchResult.model_validate(normalized_payload))
        return normalized_results

    def _build_recommendation_packages(
        self,
        *,
        request: SearchRequest,
        results: list[SearchResult],
    ) -> list[RecommendationPackage]:
        if not results and not request.destination:
            return []

        destination_order: list[str] = []
        destination_map: dict[str, list[SearchResult]] = {}

        def add_destination(label: str, result: SearchResult | None = None) -> None:
            key = label.strip()
            if not key:
                return
            if key not in destination_map:
                destination_map[key] = []
                destination_order.append(key)
            if result is not None:
                destination_map[key].append(result)

        for candidate in request.destination_candidates:
            add_destination(candidate)
        if request.destination:
            add_destination(request.destination)
        for candidate in self._generate_llm_candidate_destinations(request):
            add_destination(candidate)

        for result in results:
            if isinstance(result, FlightSearchResult):
                add_destination(request.destination or result.destination_code, result)
            else:
                add_destination(result.location_label or request.destination or result.title, result)

        packages: list[RecommendationPackage] = []
        seen_signatures: set[str] = set()
        for destination in destination_order:
            destination_results = destination_map.get(destination, [])
            fit_status = self._evaluate_hard_constraints(request, destination_results, destination)
            if not self._apply_hard_blocker_gate(fit_status):
                continue
            fallback_level = self._compute_fallback_level(fit_status, bool(destination_results))
            signature = self._generate_duplicate_signature(destination, request)
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            score = self._score_recommendation(fit_status, destination_results)
            rationale, reason_tags = self._assemble_rationale(request, fit_status, destination_results)
            estimated_cost = self._estimate_total_cost(destination_results, request)
            packages.append(
                RecommendationPackage(
                    bundle_id=f"pkg-{len(packages) + 1}",
                    destination=destination,
                    score=score,
                    rationale=rationale,
                    rationale_text=rationale[0] if rationale else None,
                    reason_tags=reason_tags,
                    estimated_total_cost=estimated_cost,
                    hard_constraint_status=fit_status,
                    fallback_level=fallback_level,
                    duplicate_signature=signature,
                )
            )

        packages.sort(
            key=lambda package: (
                {"high-fit": 2, "partial-fit": 1, "fallback": 0}.get(
                    package.fallback_level, 0
                ),
                package.score,
            ),
            reverse=True,
        )
        return packages[:3]

    def _generate_llm_candidate_destinations(self, request: SearchRequest) -> list[str]:
        if not settings.ENABLE_LLM_SUGGESTIONS or not request.query:
            return []

        lowered = request.query.lower()
        pool: list[str] = []
        if "beach" in lowered or "warm" in lowered:
            pool.extend([
                "Lisbon", "Mallorca", "Cancun",
                "Miami", "Hawaii", "The Bahamas"
            ])
        if "culture" in lowered or "city" in lowered:
            pool.extend(["Barcelona", "Lisbon", "Kyoto"])
        if "adventure" in lowered:
            pool.extend(["Reykjavik", "Queenstown"])

        deduped: list[str] = []
        seen: set[str] = set()
        for destination in pool:
            key = destination.lower()
            if key in seen:
                continue
            if not self._validate_llm_candidate(destination, request):
                continue
            seen.add(key)
            deduped.append(destination)
        return deduped[:3]

    def _validate_llm_candidate(self, destination: str, request: SearchRequest) -> bool:
        if not destination.strip():
            return False
        if request.destination and destination.lower() == request.destination.lower():
            return True
        # Hard constraints still apply to generated suggestions.
        return bool(request.date_range and request.date_range.start and request.budget_range)

    def _evaluate_hard_constraints(
        self,
        request: SearchRequest,
        destination_results: list[SearchResult],
        destination: str,
    ) -> dict[str, bool]:
        has_timeline = bool(request.date_range and request.date_range.start)
        has_budget = bool(request.budget_range and request.budget_range.maximum is not None)
        destination_known = bool(request.destination or destination)
        budget_ok = True
        if has_budget and destination_results:
            max_budget = request.budget_range.maximum if request.budget_range else None
            if max_budget is not None:
                cheapest = min(result.total_price for result in destination_results)
                budget_ok = cheapest <= max_budget
        return {
            "destination": destination_known,
            "timeline": has_timeline,
            "budget": has_budget and budget_ok,
        }

    def _apply_hard_blocker_gate(self, fit_status: dict[str, bool]) -> bool:
        # Destination and timeline are strict blockers. Budget can fall back to partial fit.
        return fit_status.get("destination", False) and fit_status.get("timeline", False)

    def _compute_fallback_level(
        self, fit_status: dict[str, bool], has_inventory: bool
    ) -> str:
        if all(fit_status.values()) and has_inventory:
            return "high-fit"
        if fit_status.get("budget", False):
            return "partial-fit"
        return "fallback"

    def _score_recommendation(
        self, fit_status: dict[str, bool], destination_results: list[SearchResult]
    ) -> float:
        base = sum(35 for met in fit_status.values() if met)
        if destination_results:
            top_score = max(result.score for result in destination_results)
            base += min(30, top_score / 3)
        return round(base, 2)

    def _assemble_rationale(
        self,
        request: SearchRequest,
        fit_status: dict[str, bool],
        destination_results: list[SearchResult],
    ) -> tuple[list[str], list[str]]:
        tags: list[str] = []
        if fit_status.get("timeline"):
            tags.append("timeline match")
        if fit_status.get("budget"):
            tags.append("budget fit")
        else:
            tags.append("best partial fit")
        if request.weather_preference and request.weather_preference.temperature:
            tags.append(f"{request.weather_preference.temperature} weather")
        if destination_results:
            best = max(destination_results, key=lambda result: result.score)
            tags.append(f"top provider score {round(best.score)}")
        tags = tags[:3]
        sentence = "Matches your key constraints with the strongest available inventory."
        if not fit_status.get("budget"):
            sentence = "Meets destination and timing constraints with the closest available budget match."
        return [sentence], tags

    def _estimate_total_cost(
        self, destination_results: list[SearchResult], request: SearchRequest
    ) -> float | None:
        if destination_results:
            return float(min(result.total_price for result in destination_results))
        if request.budget_range and request.budget_range.maximum is not None:
            return request.budget_range.maximum
        return None

    def _generate_duplicate_signature(
        self, destination: str, request: SearchRequest
    ) -> str:
        budget = (
            f"{request.budget_range.minimum}-{request.budget_range.maximum}"
            if request.budget_range
            else "no-budget"
        )
        date_key = (
            f"{request.date_range.start.isoformat()}:{request.date_range.end.isoformat() if request.date_range.end else ''}"
            if request.date_range
            else "no-dates"
        )
        return f"{destination.lower()}|{date_key}|{budget}"

    def _deterministic_flight_interleave(
        self, results: list[FlightSearchResult]
    ) -> list[FlightSearchResult]:
        if len(results) <= 1:
            return results

        provider_order = {
            provider.provider_name: index for index, provider in enumerate(self.providers)
        }
        provider_queues: dict[str, deque[FlightSearchResult]] = {}
        for result in results:
            provider_queues.setdefault(result.provider, deque()).append(result)

        merged: list[FlightSearchResult] = []
        while True:
            candidates = [
                (queue[0].score, provider)
                for provider, queue in provider_queues.items()
                if queue
            ]
            if not candidates:
                break
            _, winner = max(
                candidates,
                key=lambda item: (item[0], -provider_order.get(item[1], 10_000)),
            )
            merged.append(provider_queues[winner].popleft())
        return merged

    def _provider_cache_key(
        self, provider: TravelProvider, request: SearchRequest, inventory_type: InventoryType
    ) -> str:
        payload = request.model_dump(mode="json")
        payload["inventory"] = [inventory_type.value]
        raw = json.dumps(payload, sort_keys=True)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        return f"provider:{provider.provider_name}:{inventory_type.value}:{digest}"

    def _read_cached_provider_results(
        self, provider: TravelProvider, request: SearchRequest, inventory_type: InventoryType
    ) -> list[SearchResult] | None:
        try:
            cached = redis_client.get(self._provider_cache_key(provider, request, inventory_type))
            if not cached:
                return None
            data = json.loads(cached)
            return [self._result_from_dict(item) for item in data]
        except Exception:
            return None

    def _cache_provider_results(
        self,
        provider: TravelProvider,
        request: SearchRequest,
        inventory_type: InventoryType,
        results: list[SearchResult],
    ) -> None:
        try:
            redis_client.setex(
                self._provider_cache_key(provider, request, inventory_type),
                settings.SEARCH_CACHE_TTL_SECONDS,
                json.dumps([result.model_dump(mode="json") for result in results]),
            )
        except Exception:
            pass

    def _cache_response(self, request: SearchRequest, response: SearchResponse) -> None:
        try:
            digest = hashlib.sha256(
                json.dumps(request.model_dump(mode="json"), sort_keys=True).encode()
            ).hexdigest()
            redis_client.setex(
                f"search:{digest}",
                settings.SEARCH_CACHE_TTL_SECONDS,
                response.model_dump_json(),
            )
        except Exception:
            pass

    def _record_search(
        self,
        db,
        response: SearchResponse,
        request: SearchRequest,
        executions: list[ProviderExecution],
    ) -> None:
        if db is None:
            return
        try:
            search_run = SearchRun(
                search_id=response.search_id,
                query=request.query or "",
                inventories=[item.value for item in request.inventory],
                request_payload=request.model_dump(mode="json"),
                warnings=response.warnings,
                result_count=len(response.results),
            )
            db.add(search_run)
            db.flush()
            for execution in executions:
                db.add(
                    ProviderRun(
                        search_run_id=search_run.id,
                        provider=execution.provider.provider_name,
                        inventory_type=execution.inventory_type.value,
                        configured=execution.configured,
                        success=execution.error_message is None,
                        cache_hit=execution.cache_hit,
                        result_count=execution.result_count,
                        duration_ms=execution.duration_ms,
                        error_message=execution.error_message,
                    )
                )
            # Record user search history and upsert user preference if user_id is provided
            if getattr(request, "user_id", None) is not None:
                search_history = SearchHistory(
                    user_id=request.user_id,
                    search_id=response.search_id,
                    query=request.query or request.destination or "Discovery Search",
                )
                db.add(search_history)
                
                # Check for existing user preference
                pref = db.query(UserPreference).filter(UserPreference.user_id == request.user_id).first()
                if not pref:
                    pref = UserPreference(user_id=request.user_id)
                    db.add(pref)
                
                if request.origin:
                    pref.default_origin = request.origin
                if request.inventory:
                    pref.preferred_inventory = [item.value for item in request.inventory]
                if request.currency_code:
                    pref.currency = request.currency_code

            db.commit()
        except SQLAlchemyError:
            db.rollback()

    def _result_from_dict(self, payload: dict) -> SearchResult:
        inventory_type = payload.get("inventory_type")
        if inventory_type == InventoryType.FLIGHT.value:
            return FlightSearchResult(**payload)
        return StaySearchResult(**payload)

    def _dedupe(self, items: list[str]) -> list[str]:
        seen = []
        for item in items:
            if item and item not in seen:
                seen.append(item)
        return seen

    def _parse_date_range(self, payload: dict | None) -> SearchDateRange | None:
        if not payload:
            return None
        start = self._parse_date_value(payload.get("start"))
        end = self._parse_date_value(payload.get("end"))
        if not start:
            return None
        return SearchDateRange(start=start, end=end)

    def _parse_date_value(self, value: str | date | None) -> date | None:
        if isinstance(value, date):
            return value
        if not value:
            return None
        try:
            return date.fromisoformat(str(value))
        except ValueError:
            return None


search_service = SearchService()
