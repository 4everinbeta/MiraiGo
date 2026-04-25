import pytest

from src.app.schemas.search import (
    ClarificationAnswer,
    ClarificationSlot,
    InventoryType,
    SearchDateRange,
    SearchRequest,
)


def test_search_request_defaults():
    payload = SearchRequest(query="Trip to Tokyo")
    assert payload.inventory == [InventoryType.STAY, InventoryType.FLIGHT]
    assert payload.travelers.adults == 1


def test_search_date_range_validation():
    with pytest.raises(ValueError):
        SearchDateRange(start="2026-05-08", end="2026-05-03")


def test_search_request_requires_query_or_destination():
    with pytest.raises(ValueError):
        SearchRequest(query=None, destination=None)


def test_search_request_allows_clarification_without_query_or_destination():
    payload = SearchRequest(
        query=None,
        destination=None,
        clarification_answer=ClarificationAnswer(
            slot=ClarificationSlot.DESTINATION,
            answer_text="Portugal",
        ),
    )
    assert payload.clarification_answer is not None
