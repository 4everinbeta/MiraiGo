import asyncio
from src.app.scrapers.expedia import ExpediaScraper
from src.app.scrapers.booking import BookingScraper
from src.app.scrapers.airbnb import AirbnbScraper

async def verify():
    query = "New York"
    scrapers = [ExpediaScraper(), BookingScraper(), AirbnbScraper()]
    
    for scraper in scrapers:
        print(f"Verifying {scraper.__class__.__name__}...")
        try:
            # We use a mocked approach here or a real one if network is allowed.
            # For verification in this environment, we'll just check if they can be initialized and called.
            result = await scraper.scrape(query)
            print(f"Result from {result['provider']}: {result['results'][0]}")
        except Exception as e:
            print(f"Error with {scraper.__class__.__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
