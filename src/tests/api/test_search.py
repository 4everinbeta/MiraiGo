import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_search_endpoint_success():
    # Expedia: "beach" (10)
    mock_expedia = {"provider": "Expedia", "results": ["Beach hotel"], "query": "Miami"}
    # Booking: "luxurious" (10) + "oceanfront" (5) + "resort" (5) = 20
    mock_booking = {"provider": "Booking.com", "results": ["Luxurious oceanfront resort"], "query": "Miami"}
    # Airbnb: (0)
    mock_airbnb = {"provider": "Airbnb", "results": ["Cozy apartment"], "query": "Miami"}
    
    with patch("src.app.scrapers.expedia.ExpediaScraper.scrape", return_value=mock_expedia), \
         patch("src.app.scrapers.booking.BookingScraper.scrape", return_value=mock_booking), \
         patch("src.app.scrapers.airbnb.AirbnbScraper.scrape", return_value=mock_airbnb):
        
        response = client.get("/api/v1/search?q=Find a luxurious beach trip in Miami")
        assert response.status_code == 200
        data = response.json()
        assert data["intent"]["location"] == "Miami"
        assert data["count"] == 3
        # Booking.com should be ranked highest
        assert data["results"][0]["provider"] == "Booking.com"
        assert data["results"][0]["score"] == 20
