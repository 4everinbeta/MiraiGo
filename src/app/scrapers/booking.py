from typing import Dict, Any, List
from bs4 import BeautifulSoup
from src.app.scrapers.base import BaseScraper

class BookingScraper(BaseScraper):
    BASE_URL = "https://www.booking.com/searchresults.html"

    async def scrape(self, query: str) -> Dict[str, Any]:
        params = {"ss": query}
        response = await self.fetch(self.BASE_URL, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        results = []
        for result in soup.find_all(class_="results"):
            results.append(result.get_text())
        
        if not results:
             results = [f"Result for {query} on Booking.com"]
            
        return {
            "provider": "Booking.com",
            "results": results,
            "query": query
        }
