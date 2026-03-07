import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_search_filtering_budget():
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
        # Should only contain the cheap hotel
        assert data["count"] == 1
        assert data["results"][0]["text"] == "Cheap Hotel"

@pytest.mark.asyncio
async def test_search_filtering_amenities():
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
        # Should only contain the hotel with pool
        assert data["count"] == 1
        assert "pool" in data["results"][0]["text"].lower() or "pool" in data["results"][0].get("amenities", [])
