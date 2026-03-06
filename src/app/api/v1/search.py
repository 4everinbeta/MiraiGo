from fastapi import APIRouter, Query, Depends
from typing import List, Any, Dict
from src.app.nlp.intent import extract_intent
from src.app.scrapers.expedia import ExpediaScraper
from src.app.scrapers.booking import BookingScraper
from src.app.scrapers.airbnb import AirbnbScraper
from src.app.optimization.engine import rank_results

router = APIRouter()

@router.get("/search")
async def search(q: str = Query(..., description="Natural language travel search query")):
    # 1. Extract Intent
    intent = extract_intent(q)
    
    # 2. Scrape from multiple providers in parallel
    scrapers = [ExpediaScraper(), BookingScraper(), AirbnbScraper()]
    
    # We use asyncio.gather for parallel scraping
    import asyncio
    scraping_tasks = [scraper.scrape(intent["location"] or q) for scraper in scrapers]
    raw_results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
    
    # Flatten and process results
    all_results = []
    for res in raw_results:
        if isinstance(res, dict) and "results" in res:
            provider = res["provider"]
            for text in res["results"]:
                all_results.append({
                    "provider": provider,
                    "text": text
                })
        else:
            # Handle potential scraping errors
            pass

    # 3. Optimize and Rank
    ranked_results = rank_results(all_results, intent["qualities"])
    
    return {
        "intent": intent,
        "count": len(ranked_results),
        "results": ranked_results
    }
