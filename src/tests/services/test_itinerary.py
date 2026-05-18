import pytest

from src.app.data.cost_bands import destination_to_region_key, estimate_cost
from src.app.schemas.itinerary import ItineraryProposeRequest
from src.app.schemas.search import TravelerCounts
from src.app.services.itinerary import itinerary_service


@pytest.mark.asyncio
async def test_propose_returns_ranked_itinerary_proposals():
    request = ItineraryProposeRequest(
        query=(
            "Given a total budget of $6000-$7500 for a family of three this summer, "
            "considering Vancouver Island, New England, or Pacific Northwest"
        ),
        candidate_destinations=["Vancouver Island", "New England", "Pacific Northwest"],
    )

    response = await itinerary_service.propose(request)

    assert 2 <= len(response.proposals) <= 4
    assert all(item.destination for item in response.proposals)
    assert all(item.cost_estimate.total_estimated > 0 for item in response.proposals)
    assert all(item.within_budget is True or item.over_budget_note for item in response.proposals)


def test_estimate_cost_returns_positive_totals():
    estimate = estimate_cost(
        "new-england",
        "summer",
        TravelerCounts(adults=2, children=1, infants=0),
        duration_nights=7,
        include_car=True,
    )
    assert estimate.total_estimated > 0
    assert estimate.flight_estimated > 0
    assert estimate.stay_estimated > 0


def test_destination_to_region_key_matches_known_location():
    assert destination_to_region_key("Vancouver Island") == "vancouver-island"


@pytest.mark.asyncio
async def test_propose_missing_budget_returns_clarification():
    request = ItineraryProposeRequest(
        query="I want to travel somewhere nice",
        candidate_destinations=["Pacific Northwest"],
    )

    response = await itinerary_service.propose(request)

    assert response.proposals == []
    assert response.clarification_state is not None


@pytest.mark.asyncio
async def test_propose_with_clarification_answer_resolves_to_proposals():
    request = ItineraryProposeRequest(
        query="I want to travel somewhere nice",
        candidate_destinations=["Pacific Northwest"],
        clarification_answer={
            "slot": "budget",
            "answer_text": "$6000-$7500",
            "explicit_unknown": False,
        },
    )

    response = await itinerary_service.propose(request)

    assert len(response.proposals) >= 1
