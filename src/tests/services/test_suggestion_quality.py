from src.app.schemas.search import (
    ClarificationBudgetRange,
    FlightSearchResult,
    InventoryType,
    SearchDateRange,
    SearchRequest,
)
from src.app.core.config import settings
from src.app.services.search import SearchService


def _flight_result(
    *,
    destination_code: str,
    total_price: float,
    score: float = 90,
) -> FlightSearchResult:
    return FlightSearchResult(
        inventory_type=InventoryType.FLIGHT,
        provider="duffel",
        provider_label="Duffel",
        title=f"DEN to {destination_code}",
        description="Test flight",
        total_price=total_price,
        currency="USD",
        score=score,
        origin_code="DEN",
        destination_code=destination_code,
        departure_at="2026-06-05T10:00:00",
        arrival_at="2026-06-05T19:00:00",
        carrier_codes=["TP"],
        stops=1,
        duration="PT9H",
    )


def test_hard_blockers_gate_recommendation_generation():
    service = SearchService()
    request = SearchRequest(
        query="Trip options",
        destination="Lisbon",
        budget_range=ClarificationBudgetRange(minimum=1000, maximum=2000, currency_code="USD"),
    )
    packages = service._build_recommendation_packages(
        request=request,
        results=[_flight_result(destination_code="LIS", total_price=1200)],
    )

    assert packages == []


def test_high_fit_and_partial_fit_labels_are_assigned():
    service = SearchService()
    request = SearchRequest(
        query="Trip options",
        destination="Lisbon",
        date_range=SearchDateRange(start="2026-06-05", end="2026-06-12"),
        budget_range=ClarificationBudgetRange(minimum=1000, maximum=1500, currency_code="USD"),
    )
    packages = service._build_recommendation_packages(
        request=request,
        results=[_flight_result(destination_code="LIS", total_price=1800)],
    )

    assert len(packages) == 1
    assert packages[0].fallback_level == "fallback"
    assert packages[0].hard_constraint_status["destination"] is True
    assert packages[0].hard_constraint_status["timeline"] is True
    assert packages[0].hard_constraint_status["budget"] is False


def test_duplicate_signature_deduplicates_equivalent_suggestions():
    service = SearchService()
    request = SearchRequest(
        query="Trip options",
        destination_candidates=["Lisbon", "Lisbon"],
        destination="Lisbon",
        date_range=SearchDateRange(start="2026-06-05", end="2026-06-12"),
        budget_range=ClarificationBudgetRange(minimum=1000, maximum=2500, currency_code="USD"),
    )
    packages = service._build_recommendation_packages(request=request, results=[])

    assert len(packages) == 1
    signatures = [item.duplicate_signature for item in packages]
    assert len(signatures) == len(set(signatures))


def test_recap_edit_style_budget_shift_refreshes_rationale_tags():
    service = SearchService()
    request = SearchRequest(
        query="Warm beach trip",
        destination="Lisbon",
        date_range=SearchDateRange(start="2026-06-05", end="2026-06-12"),
        budget_range=ClarificationBudgetRange(minimum=1000, maximum=1200, currency_code="USD"),
    )
    packages = service._build_recommendation_packages(
        request=request,
        results=[_flight_result(destination_code="LIS", total_price=1800)],
    )

    assert packages
    assert packages[0].fallback_level == "fallback"
    assert "best partial fit" in packages[0].reason_tags


def test_llm_candidate_guardrail_rejects_when_hard_constraints_missing():
    service = SearchService()
    previous = settings.ENABLE_LLM_SUGGESTIONS
    settings.ENABLE_LLM_SUGGESTIONS = True
    try:
        request = SearchRequest(query="Warm beach trip with culture")
        assert service._generate_llm_candidate_destinations(request) == []
    finally:
        settings.ENABLE_LLM_SUGGESTIONS = previous
