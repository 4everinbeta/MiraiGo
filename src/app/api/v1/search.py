from fastapi import APIRouter, Query, Depends
from typing import List, Any, Dict, Optional
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
async def search(
    q: str = Query(..., description="Natural language travel search query"),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    amenities: Optional[str] = Query(None, description="Comma-separated list of amenities"),
    modes: Optional[str] = Query(None, description="Comma-separated list of travel modes")
):
    # 1. Check Cache (Simplified key for now, doesn't include all filters)
    cache_key = f"search:{q.lower().strip()}:{min_price}:{max_price}:{amenities}:{modes}"
    try:
        cached_results = redis_client.get(cache_key)
        if cached_results:
            return json.loads(cached_results)
    except Exception:
        pass

    # 2. Extract Intent
    intent = extract_intent(q)
    
    # 3. Scrape from multiple providers in parallel
    scrapers = [ExpediaScraper(), BookingScraper(), AirbnbScraper()]
    
    scraping_tasks = [scraper.scrape(intent["location"] or q) for scraper in scrapers]
    raw_results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
    
    # 4. Flatten and process results
    all_results = []
    for res in raw_results:
        if isinstance(res, dict) and "results" in res:
            provider = res.get("provider", "Unknown")
            for item in res["results"]:
                if isinstance(item, str):
                    result_item = {
                        "provider": provider,
                        "text": item,
                        "price": None,
                        "amenities": []
                    }
                else:
                    result_item = {
                        "provider": provider,
                        "text": item.get("text", ""),
                        "price": item.get("price"),
                        "amenities": item.get("amenities", [])
                    }
                    # Include other fields
                    result_item.update({k: v for k, v in item.items() if k not in ["text", "price", "amenities"]})
                all_results.append(result_item)

    # 5. Apply Backend Filters
    filtered_results = all_results
    
    if max_price is not None:
        filtered_results = [r for r in filtered_results if r.get("price") is None or r.get("price") <= max_price]
    
    if min_price is not None:
        filtered_results = [r for r in filtered_results if r.get("price") is None or r.get("price") >= min_price]
        
    if amenities:
        target_amenities = [a.strip().lower() for a in amenities.split(",")]
        filtered_results = [
            r for r in filtered_results 
            if any(ta in [ra.lower() for ra in r.get("amenities", [])] for ta in target_amenities)
        ]

    # 6. Optimize and Rank
    ranked_results = rank_results(filtered_results, intent["qualities"])
    
    response_data = {
        "intent": intent,
        "count": len(ranked_results),
        "results": ranked_results
    }

    # 7. Store in Cache (1 hour expiry)
    try:
        redis_client.setex(cache_key, 3600, json.dumps(response_data))
    except Exception:
        pass
    
    return response_data
