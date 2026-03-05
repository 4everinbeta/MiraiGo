import re
from typing import Dict, List, Any

QUALITIES = [
    "warm", "beach", "mountains", "amusement parks", "family friendly",
    "luxurious", "budget", "romantic", "quiet", "hiking", "skiing"
]

DATES = [
    "December", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November",
    "summer", "winter", "spring", "fall", "next year", "next month"
]

def extract_intent(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    # Simple Location Extraction (Look for "to", "in", "near" followed by capitalized words)
    # This is a very basic heuristic.
    location = None
    location_match = re.search(r'(?:to|in|near)\s+([A-Z][a-z]+)', query)
    if location_match:
        location = location_match.group(1)
    elif "miami" in query_lower:
        location = "Miami"
    elif "denver" in query_lower:
        location = "Denver"

    # Qualities Extraction
    found_qualities = []
    for quality in QUALITIES:
        if quality in query_lower:
            found_qualities.append(quality)
            
    # Dates Extraction
    found_dates = []
    for date in DATES:
        if date.lower() in query_lower:
            found_dates.append(date)
            
    return {
        "location": location,
        "qualities": found_qualities,
        "dates": found_dates,
        "original_query": query
    }
