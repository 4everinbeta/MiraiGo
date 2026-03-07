from typing import List, Dict, Any

SYNONYMS = {
    "warm": ["sunny", "hot", "tropical"],
    "beach": ["seaside", "oceanfront", "coastal", "villa", "resort"],
    "mountains": ["alpine", "ski", "hiking", "cabin"],
    "family friendly": ["kids", "playground", "pool"],
    "luxurious": ["5-star", "premium", "deluxe"],
}

def rank_results(results: List[Dict[str, Any]], qualities: List[str]) -> List[Dict[str, Any]]:
    scored_results = []
    
    for result in results:
        score = 0
        raw_text = result.get("text", "")
        text = str(raw_text).lower()
        
        for quality in qualities:
            quality_lower = quality.lower()
            if quality_lower in text:
                score += 10
            
            # Synonym matching
            if quality_lower in SYNONYMS:
                for synonym in SYNONYMS[quality_lower]:
                    if synonym in text:
                        score += 5
        
        result["score"] = score
        scored_results.append(result)
        
    # Sort by score (descending)
    return sorted(scored_results, key=lambda x: x["score"], reverse=True)
