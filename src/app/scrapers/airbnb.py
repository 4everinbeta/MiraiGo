from typing import Dict, Any, List
from bs4 import BeautifulSoup
from src.app.scrapers.base import BaseScraper

class AirbnbScraper(BaseScraper):
    BASE_URL = "https://www.airbnb.com/s/homes"

    async def scrape(self, query: str) -> Dict[str, Any]:
        params = {"query": query}
        response = await self.fetch(self.BASE_URL, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        results = []
        for result in soup.find_all(class_="results"):
            results.append(result.get_text())
        
        if not results:
             results = [f"Result for {query} on Airbnb"]
            
        return {
            "provider": "Airbnb",
            "results": results,
            "query": query
        }
