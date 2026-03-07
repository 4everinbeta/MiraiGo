import pytest
from pydantic import ValidationError
from src.app.schemas.search import DateRange, SearchFilterParams

def test_date_range_valid():
    dr = DateRange(start="2026-01-01", end="2026-01-15")
    assert dr.start == "2026-01-01"
    assert dr.end == "2026-01-15"

def test_search_filter_params_valid():
    filters = SearchFilterParams(max_price=500, amenities=["pool", "wifi"])
    assert filters.max_price == 500
    assert "pool" in filters.amenities

def test_search_filter_params_optional():
    filters = SearchFilterParams()
    assert filters.max_price is None
    assert filters.amenities == []
