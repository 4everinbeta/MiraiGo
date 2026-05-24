from fastapi.testclient import TestClient

from src.app.main import app
from src.app.providers.base import ProviderError, TravelProvider
from src.app.schemas.search import FlightSearchResult, InventoryType, SearchRequest, StaySearchResult
from src.app.services.search import search_service

client = TestClient(app)


class ConfiguredProvider(TravelProvider):
    provider_name = "testlive"
    display_name = "Test Live"
    inventory_types = (InventoryType.STAY, InventoryType.FLIGHT)

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        if inventory_type == InventoryType.STAY:
            return [
                StaySearchResult(
                    inventory_type=InventoryType.STAY,
                    provider=self.provider_name,
                    provider_label=self.display_name,
                    title=f"Stay in {request.destination}",
                    description="Live stay result",
                    total_price=900,
                    currency="USD",
                    redirect_url="https://example.com/stay",
                    deep_link_label="Continue search",
                    score=84,
                    location_label=request.destination,
                    amenities=["wifi", "breakfast"],
                    nightly_price=180,
                    check_in=request.date_range.start.isoformat() if request.date_range else None,
                    check_out=request.date_range.end.isoformat() if request.date_range and request.date_range.end else None,
                )
            ]
        return [
            FlightSearchResult(
                inventory_type=InventoryType.FLIGHT,
                provider=self.provider_name,
                provider_label=self.display_name,
                title=f"{request.origin} to {request.destination}",
                description="Live flight result",
                total_price=640,
                currency="USD",
                redirect_url="https://example.com/flight",
                deep_link_label="Continue search",
                score=92,
                origin_code="DEN",
                destination_code="BCN",
                departure_at="2026-05-03T09:30:00",
                arrival_at="2026-05-03T20:15:00",
                carrier_codes=["TP"],
                stops=1,
                duration="PT10H45M",
            )
        ]


class DisabledProvider(TravelProvider):
    provider_name = "disabled"
    display_name = "Disabled Provider"
    inventory_types = (InventoryType.STAY,)

    @property
    def is_configured(self) -> bool:
        return False

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        return []


class EmptyFlightProvider(TravelProvider):
    provider_name = "emptyflight"
    display_name = "Empty Flight"
    inventory_types = (InventoryType.FLIGHT,)

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        return []


class PartialFailureFlightProvider(TravelProvider):
    provider_name = "partialfail"
    display_name = "Partial Failure"
    inventory_types = (InventoryType.FLIGHT,)

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        raise ProviderError("upstream timeout")


class SparseFlightProvider(TravelProvider):
    provider_name = "sparseflight"
    display_name = "Sparse Flight"
    inventory_types = (InventoryType.FLIGHT,)

    @property
    def is_configured(self) -> bool:
        return True

    async def search(self, request: SearchRequest, inventory_type: InventoryType):
        return [
            FlightSearchResult(
                inventory_type=InventoryType.FLIGHT,
                provider=self.provider_name,
                provider_label=self.display_name,
                title=f"{request.origin} to {request.destination}",
                description="Sparse flight result",
                total_price=640,
                currency="USD",
                score=75,
                origin_code="DEN",
                destination_code="BCN",
                departure_at="",
                arrival_at="",
                carrier_codes=["TP"],
                stops=0,
                duration=None,
            )
        ]


def test_post_search_returns_canonical_results():
    search_service.providers = [ConfiguredProvider(), DisabledProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Barcelona trip from Denver",
            "destination": "Barcelona",
            "origin": "Denver",
            "inventory": ["stay", "flight"],
            "date_range": {"start": "2026-05-03", "end": "2026-05-08"},
            "trip_length_days": 5,
            "budget_range": {"minimum": 800, "maximum": 2000, "currency_code": "USD"},
            "weather_preference": {"temperature": "warm", "source_text": "warm weather"},
            "travelers": {"adults": 2, "children": 0, "infants": 0},
            "stay_filters": {"max_price": 1200, "amenities": ["wifi"]},
            "flight_filters": {"max_price": 1200, "nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["search_id"]
    assert len(payload["results"]) == 2
    assert payload["recommendation_packages"]
    assert {item["inventory_type"] for item in payload["results"]} == {"stay", "flight"}
    flight_offer = next(item for item in payload["results"] if item["inventory_type"] == "flight")
    assert flight_offer["price_minor"] == 64000
    assert flight_offer["currency_code"] == "USD"
    assert flight_offer["duration_minutes"] == 645
    assert flight_offer["stops_count"] == 1
    assert flight_offer["normalized_offer_id"]
    assert "provider_offer_id" in flight_offer
    assert isinstance(flight_offer["missing_fields"], list)
    assert flight_offer["conversion_status"] == "native"
    assert set(flight_offer["airfare_provenance"].keys()) == {
        "source_provider",
        "provider_offer_id",
        "source_quote_at",
        "source_payload_ref",
    }
    assert set(flight_offer["airfare_freshness"].keys()) == {
        "freshness_source",
        "freshness_at",
        "fetched_at",
    }
    assert flight_offer["total_price"] == 640
    assert flight_offer["currency"] == "USD"
    assert flight_offer["stops"] == 1
    assert flight_offer["duration"] == "PT10H45M"
    assert any(status["provider"] == "testlive" and status["configured"] for status in payload["provider_status"])
    assert any(status["provider"] == "disabled" and not status["configured"] for status in payload["provider_status"])


def test_post_search_keeps_null_present_normalized_contract_for_sparse_offers():
    search_service.providers = [SparseFlightProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Barcelona trip from Denver",
            "destination": "Barcelona",
            "origin": "Denver",
            "inventory": ["flight"],
            "date_range": {"start": "2026-05-03", "end": "2026-05-08"},
            "trip_length_days": 5,
            "budget_range": {"minimum": 800, "maximum": 2000, "currency_code": "USD"},
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    offer = response.json()["results"][0]
    assert offer["duration_minutes"] is None
    assert offer["normalized_offer_id"] is None
    assert "departure_at" in offer["missing_fields"]
    assert "arrival_at" in offer["missing_fields"]
    assert "duration_minutes" in offer["missing_fields"]


def test_post_search_keeps_normalized_offer_id_stable_across_repeated_calls():
    search_service.providers = [ConfiguredProvider()]
    payload = {
        "query": "Barcelona trip from Denver",
        "destination": "Barcelona",
        "origin": "Denver",
        "inventory": ["flight"],
        "date_range": {"start": "2026-05-03", "end": "2026-05-08"},
        "trip_length_days": 5,
        "budget_range": {"minimum": 800, "maximum": 2000, "currency_code": "USD"},
        "travelers": {"adults": 1, "children": 0, "infants": 0},
        "stay_filters": {"amenities": []},
        "flight_filters": {"nonstop": False},
        "currency_code": "USD",
        "limit_per_provider": 5,
    }

    first = client.post("/api/v1/search", json=payload)
    second = client.post("/api/v1/search", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    first_offer = first.json()["results"][0]
    second_offer = second.json()["results"][0]
    assert first_offer["normalized_offer_id"] == second_offer["normalized_offer_id"]


def test_post_search_handles_no_configured_providers():
    search_service.providers = [DisabledProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Trip to Lisbon",
            "destination": "Lisbon",
            "inventory": ["stay"],
            "date_range": {"start": "2026-08-01", "end": "2026-08-08"},
            "trip_length_days": 7,
            "budget_range": {"minimum": 500, "maximum": 1800, "currency_code": "USD"},
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"] == []
    assert payload["warnings"]


def test_post_search_returns_clarification_state_with_weather():
    search_service.providers = [DisabledProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Need warm weather trip ideas",
            "inventory": ["stay"],
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["clarification_state"] is not None
    assert payload["clarification_state"]["weather"] is not None
    assert payload["clarification_state"]["weather"]["slot"] == "weather"
    assert payload["clarification_state"]["weather"]["explicit_unknown"] is False
    assert payload["clarification_state"]["weather"]["source_text"] in {"warm weather", "warm"}


def test_post_search_warns_when_flight_provider_returns_no_offers():
    search_service.providers = [EmptyFlightProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Barcelona trip from Denver",
            "destination": "Barcelona",
            "origin": "Denver",
            "inventory": ["flight"],
            "date_range": {"start": "2026-05-03", "end": "2026-05-08"},
            "trip_length_days": 5,
            "budget_range": {"minimum": 800, "maximum": 2000, "currency_code": "USD"},
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"] == []
    assert any("returned no flight offers" in warning for warning in payload["warnings"])


def test_post_search_partial_dual_provider_failure_keeps_available_results():
    search_service.providers = [ConfiguredProvider(), PartialFailureFlightProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Barcelona trip from Denver",
            "destination": "Barcelona",
            "origin": "Denver",
            "inventory": ["flight"],
            "date_range": {"start": "2026-05-03", "end": "2026-05-08"},
            "trip_length_days": 5,
            "budget_range": {"minimum": 800, "maximum": 2000, "currency_code": "USD"},
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert [item["provider"] for item in payload["results"]] == ["testlive"]
    assert any("Partial Failure flight search unavailable: upstream timeout" == warning for warning in payload["warnings"])
    assert any(
        status["provider"] == "partialfail"
        and status["healthy"] is False
        and status["reason"] == "upstream timeout"
        for status in payload["provider_status"]
    )
    assert any(
        status["provider"] == "testlive"
        and status["configured"] is True
        and status["healthy"] is True
        for status in payload["provider_status"]
    )


def test_post_search_multilingual_destination_and_synonym_keep_clarification_flow():
    search_service.providers = [DisabledProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Quiero un viaje economico para lisboa con playa",
            "inventory": ["stay"],
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["clarification_state"] is not None
    assert payload["clarification_state"]["destination"] is not None
    assert payload["clarification_state"]["destination"]["value_label"] == "Lisboa"
    assert payload["clarification_state"]["next_question"] is not None
    # INTENT-02: extraction remains stable and moves clarification away from already-resolved slots.
    assert payload["clarification_state"]["next_question"]["slot"] != "destination"


def test_search_handles_follow_up_clarification_turn():
    search_service.providers = [DisabledProvider()]

    first_response = client.post(
        "/api/v1/search",
        json={
            "query": "Warm beach trip in June",
            "destination": "Honolulu",
            "date_range": {"start": "2026-06-10", "end": "2026-06-17"},
            "inventory": ["stay"],
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert first_response.status_code == 200
    first_payload = first_response.json()
    assert first_payload["clarification_state"] is not None
    assert first_payload["clarification_state"]["next_question"] is not None
    assert first_payload["clarification_state"]["next_question"]["slot"] == "trip_length"

    follow_up_response = client.post(
        "/api/v1/search",
        json={
            "query": "Warm beach trip in June",
            "destination": "Honolulu",
            "date_range": {"start": "2026-06-10", "end": "2026-06-17"},
            "trip_length_days": 7,
            "clarification_answer": {
                "slot": "trip_length",
                "answer_text": "7 days",
                "explicit_unknown": False,
            },
            "inventory": ["stay"],
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert follow_up_response.status_code == 200
    follow_up_payload = follow_up_response.json()
    assert follow_up_payload["clarification_state"] is not None
    assert follow_up_payload["clarification_state"]["trip_length"]["value_label"] is not None
    assert follow_up_payload["clarification_state"]["next_question"] is not None
    # INTENT-03 / INTENT-04: follow-up turn progression remains focused and deterministic.
    assert follow_up_payload["clarification_state"]["next_question"]["slot"] == "budget"
    assert follow_up_payload["clarification_state"]["next_question"]["slot"] != "destination"


def test_post_search_returns_deterministic_flight_requirement_guidance_when_continue_is_blocked():
    search_service.providers = [DisabledProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Lisbon trip in June for 7 days under $2,500",
            "destination": "Lisbon",
            "date_range": {"start": "2026-06-01", "end": "2026-06-08"},
            "trip_length_days": 7,
            "budget_range": {"minimum": 1500, "maximum": 2500, "currency_code": "USD"},
            "inventory": ["flight"],
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["clarification_state"] is not None
    assert payload["clarification_state"]["flight_requirements_pending"] == ["origin"]
    assert (
        payload["clarification_state"]["continue_block_reason"]
        == "Continue needs origin before flight recommendations can load."
    )
    assert (
        "Flight recommendations are paused until you provide: origin."
        in payload["warnings"]
    )


def test_post_search_constraint_updates_origin_clears_continue_block_reason():
    search_service.providers = [DisabledProvider()]

    blocked_payload = {
        "query": "Lisbon trip in June for 7 days under $2,500",
        "destination": "Lisbon",
        "date_range": {"start": "2026-06-01", "end": "2026-06-08"},
        "trip_length_days": 7,
        "budget_range": {"minimum": 1500, "maximum": 2500, "currency_code": "USD"},
        "inventory": ["flight"],
        "travelers": {"adults": 1, "children": 0, "infants": 0},
        "stay_filters": {"amenities": []},
        "flight_filters": {"nonstop": False},
        "currency_code": "USD",
        "limit_per_provider": 5,
    }

    blocked_response = client.post("/api/v1/search", json=blocked_payload)
    assert blocked_response.status_code == 200
    blocked_state = blocked_response.json()["clarification_state"]
    assert blocked_state["flight_requirements_pending"] == ["origin"]
    assert blocked_state["continue_block_reason"] is not None

    follow_up_response = client.post(
        "/api/v1/search",
        json={
            **blocked_payload,
            "clarification_state": blocked_state,
            "constraint_updates": {"origin": "Denver"},
        },
    )

    assert follow_up_response.status_code == 200
    follow_up_state = follow_up_response.json()["clarification_state"]
    assert follow_up_state["flight_requirements_pending"] == []
    assert follow_up_state["continue_block_reason"] is None


def test_post_search_reports_date_range_requirement_when_continue_is_blocked():
    search_service.providers = [DisabledProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Lisbon trip for 7 days under $2,500",
            "destination": "Lisbon",
            "origin": "Denver",
            "trip_length_days": 7,
            "budget_range": {"minimum": 1500, "maximum": 2500, "currency_code": "USD"},
            "inventory": ["flight"],
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["clarification_state"] is not None
    assert payload["clarification_state"]["flight_requirements_pending"] == ["date_range"]
    assert (
        payload["clarification_state"]["continue_block_reason"]
        == "Continue needs date_range before flight recommendations can load."
    )


def test_post_search_constraint_updates_date_range_clears_continue_block_reason():
    search_service.providers = [DisabledProvider()]

    blocked_payload = {
        "query": "Lisbon trip for 7 days under $2,500",
        "destination": "Lisbon",
        "origin": "Denver",
        "trip_length_days": 7,
        "budget_range": {"minimum": 1500, "maximum": 2500, "currency_code": "USD"},
        "inventory": ["flight"],
        "travelers": {"adults": 1, "children": 0, "infants": 0},
        "stay_filters": {"amenities": []},
        "flight_filters": {"nonstop": False},
        "currency_code": "USD",
        "limit_per_provider": 5,
    }

    blocked_response = client.post("/api/v1/search", json=blocked_payload)
    assert blocked_response.status_code == 200
    blocked_state = blocked_response.json()["clarification_state"]
    assert blocked_state["flight_requirements_pending"] == ["date_range"]
    assert blocked_state["continue_block_reason"] is not None

    follow_up_response = client.post(
        "/api/v1/search",
        json={
            **blocked_payload,
            "clarification_state": blocked_state,
            "constraint_updates": {"date_range": {"start": "2026-06-01", "end": "2026-06-08"}},
        },
    )

    assert follow_up_response.status_code == 200
    follow_up_state = follow_up_response.json()["clarification_state"]
    assert follow_up_state["flight_requirements_pending"] == []
    assert follow_up_state["continue_block_reason"] is None


def test_post_search_airfare_natural_prompt_captures_route_and_timeline_without_silent_empty_results():
    search_service.providers = [ConfiguredProvider()]

    response = client.post(
        "/api/v1/search",
        json={
            "query": "Need airfare from Denver to Lisbon around early summer",
            "inventory": ["flight"],
            "travelers": {"adults": 1, "children": 0, "infants": 0},
            "stay_filters": {"amenities": []},
            "flight_filters": {"nonstop": False},
            "currency_code": "USD",
            "limit_per_provider": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"]
    assert payload["results"][0]["inventory_type"] == "flight"
    assert payload["applied_filters"]["origin"] == "Denver"
    assert payload["applied_filters"]["destination"] == "Lisbon"
    assert payload["applied_filters"]["date_range"] is not None
    assert payload["clarification_state"]["flight_requirements_pending"] == []
    assert payload["clarification_state"]["continue_block_reason"] is None
