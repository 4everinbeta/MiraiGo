import pytest
from datetime import date

from src.app.nlp.intent import extract_intent
from src.app.schemas.search import InventoryType, SearchRequest, TravelerCounts
from src.app.services.search import SearchService


def test_origin_not_falsely_extracted_as_destination():
    # Denver is preceded by 'from', so it should be the origin, NOT the destination
    query = "I want a warm beach trip in July for seven days from denver colorado"
    intent = extract_intent(query)
    
    assert intent["location"] is None  # Discovery query, destination is not specified
    assert intent["origin_hint"] == "Denver Colorado"


def test_standalone_origin_extraction():
    query = "Flights in July from Denver"
    intent = extract_intent(query)
    
    assert intent["location"] is None
    assert intent["origin_hint"] == "Denver"


def test_month_and_duration_timeline_resolution():
    query = "I want a warm beach trip in July for seven days from denver colorado"
    intent = extract_intent(query)
    
    timeline = intent["normalized_timeline"]
    assert timeline is not None
    assert timeline["precision"] == "month"
    assert timeline["window"]["start"] == "2026-07-01"
    # Duration is 7 days, so end date is 2026-07-08
    # Wait, let's check how the duration updates the end date in the search service resolve_request or intent.py
    # We will verify that duration_days is correctly parsed
    assert intent["duration_days"] == 7


@pytest.mark.asyncio
async def test_traveler_count_extraction_updates_request():
    service = SearchService()
    
    # Query with a family of four should update SearchRequest traveler counts (2 adults, 2 children)
    request = SearchRequest(
        query="Flights to Lisbon for a family of four",
        destination="Lisbon",
        inventory=[InventoryType.FLIGHT],
    )
    
    # Run SearchService._resolve_request (or search) and check resolved request
    resolved_request, _, _ = service._resolve_request(request)
    assert resolved_request.travelers.adults == 2
    assert resolved_request.travelers.children == 2


@pytest.mark.asyncio
async def test_warm_beach_discovery_suggestions():
    service = SearchService()
    
    # A warm beach query should return Miami, Hawaii, and Bahamas in suggestions
    request = SearchRequest(
        query="warm beach trip",
        inventory=[InventoryType.FLIGHT],
    )
    
    response = await service.search(request)
    suggestions = response.clarification_state.destination_suggestions
    suggested_names = {s.label for s in suggestions}
    
    assert "Miami" in suggested_names
    assert "Hawaii" in suggested_names
    assert "The Bahamas" in suggested_names or "Bahamas" in suggested_names
