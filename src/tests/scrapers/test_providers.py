import pytest
from unittest.mock import patch, MagicMock
from src.app.scrapers.booking import BookingScraper
from src.app.scrapers.airbnb import AirbnbScraper

@pytest.mark.asyncio
async def test_booking_scrape_success():
    scraper = BookingScraper()
    mock_response = MagicMock()
    mock_response.text = "<html><body><div class='results'>Hotel in LON for $200</div></body></html>"
    with patch.object(BookingScraper, 'fetch', return_value=mock_response):
        result = await scraper.scrape("LON")
        assert "LON" in result["results"][0]
        assert result["provider"] == "Booking.com"

@pytest.mark.asyncio
async def test_airbnb_scrape_success():
    scraper = AirbnbScraper()
    mock_response = MagicMock()
    mock_response.text = "<html><body><div class='results'>Apartment in PAR for $150</div></body></html>"
    with patch.object(AirbnbScraper, 'fetch', return_value=mock_response):
        result = await scraper.scrape("PAR")
        assert "PAR" in result["results"][0]
        assert result["provider"] == "Airbnb"
