from fastapi import APIRouter, Query, Depends
from typing import List, Any, Dict
import json
import asyncio
from src.app.nlp.intent import extract_intent
from src.app.scrapers.expedia import ExpediaScraper
from src.app.scrapers.booking import BookingScraper
from src.app.scrapers.airbnb import AirbnbScraper
from src.app.optimization.engine import rank_results
from src.app.db.redis import redis_client

router = APIRouter()

@router.get("/search")
async def search(q: str = Query(..., description="Natural language travel search query")):
    # 1. Check Cache
    cache_key = f"search:{q.lower().strip()}"
    try:
        cached_results = redis_client.get(cache_key)
        if cached_results:
            return json.loads(cached_results)
    except Exception:
        # If redis is down, proceed without cache
        pass

    # 2. Extract Intent
    intent = extract_intent(q)
    
    # 3. Scrape from multiple providers in parallel
    scrapers = [ExpediaScraper(), BookingScraper(), AirbnbScraper()]
    
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

    # 4. Optimize and Rank
    ranked_results = rank_results(all_results, intent["qualities"])
    
    response_data = {
        "intent": intent,
        "count": len(ranked_results),
        "results": ranked_results
    }

    # 5. Store in Cache (1 hour expiry)
    try:
        redis_client.setex(cache_key, 3600, json.dumps(response_data))
    except Exception:
        pass
    
    return response_data
