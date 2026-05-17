import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_search_filtering_budget():
    # Mock scrapers to return results with prices
    mock_expedia = {
        "provider": "Expedia",
        "results": [
            {"text": "Cheap Hotel", "price": 100},
            {"text": "Expensive Hotel", "price": 1000}
        ]
    }
    
    with patch("src.app.scrapers.expedia.ExpediaScraper.scrape", return_value=mock_expedia), \
         patch("src.app.scrapers.booking.BookingScraper.scrape", return_value={"provider": "Booking.com", "results": []}), \
         patch("src.app.scrapers.airbnb.AirbnbScraper.scrape", return_value={"provider": "Airbnb", "results": []}):
        
        # Test max_price filter
        response = client.get("/api/v1/search?q=Paris&max_price=500")
        assert response.status_code == 200
        data = response.json()
        assert "applied_filters" in data
        assert data["applied_filters"]["stay_filters"]["max_price"] == 500.0

def test_search_filtering_amenities():
    # Mock scrapers to return results with amenities
    mock_booking = {
        "provider": "Booking.com",
        "results": [
            {"text": "Hotel with Pool", "amenities": ["pool", "wifi"]},
            {"text": "Hotel with Wifi only", "amenities": ["wifi"]}
        ]
    }
    
    with patch("src.app.scrapers.expedia.ExpediaScraper.scrape", return_value={"provider": "Expedia", "results": []}), \
         patch("src.app.scrapers.booking.BookingScraper.scrape", return_value=mock_booking), \
         patch("src.app.scrapers.airbnb.AirbnbScraper.scrape", return_value={"provider": "Airbnb", "results": []}):
        
        # Test amenities filter
        response = client.get("/api/v1/search?q=London&amenities=pool")
        assert response.status_code == 200
        data = response.json()
        assert "applied_filters" in data
        assert "pool" in data["applied_filters"]["stay_filters"]["amenities"]
