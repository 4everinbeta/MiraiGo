import pytest
from unittest.mock import patch, MagicMock
from src.app.scrapers.expedia import ExpediaScraper

@pytest.mark.asyncio
async def test_expedia_scrape_success():
    scraper = ExpediaScraper()
    mock_response = MagicMock()
    mock_response.text = "<html><body><div class='results'>Flight from NYC to LON for $500</div></body></html>"
    
    with patch.object(ExpediaScraper, 'fetch', return_value=mock_response):
        result = await scraper.scrape("NYC to LON")
        assert "NYC to LON" in result["results"][0]
        assert result["provider"] == "Expedia"
