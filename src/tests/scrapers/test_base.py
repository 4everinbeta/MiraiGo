import pytest
import httpx
from src.app.scrapers.base import BaseScraper

class MockScraper(BaseScraper):
    async def scrape(self, query):
        return {"data": "test"}

def test_base_scraper_user_agent():
    scraper = MockScraper()
    assert "User-Agent" in scraper.get_headers()
    assert scraper.get_headers()["User-Agent"] is not None

@pytest.mark.asyncio
async def test_base_scraper_scrape():
    scraper = MockScraper()
    result = await scraper.scrape("test query")
    assert result == {"data": "test"}

@pytest.mark.asyncio
async def test_base_scraper_fetch_error():
    scraper = MockScraper(retries=1)
    # Using a non-existent local port to trigger RequestError
    with pytest.raises(httpx.RequestError):
        await scraper.fetch("http://localhost:1")
