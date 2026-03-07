import re
from typing import Dict, List, Any

QUALITIES = [
    "warm", "beach", "mountains", "mountain", "amusement parks", "family friendly",
    "luxurious", "budget", "romantic", "quiet", "hiking", "skiing"
]

DATES = [
    "December", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November",
    "summer", "winter", "spring", "fall", "next year", "next month"
]

# Common cities for better extraction
COMMON_CITIES = [
    "Paris", "London", "Tokyo", "New York", "Miami", "Denver", "Rome", "Barcelona", "Berlin", "Dubai"
]

def extract_intent(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    # 1. Try explicit location keywords (to|in|near|at)
    location = None
    location_match = re.search(r'(?:to|in|near|at)\s+([A-Z][a-z]+)', query)
    if location_match:
        location = location_match.group(1)
    
    # 2. If no explicit match, try finding common cities directly
    if not location:
        for city in COMMON_CITIES:
            if city.lower() in query_lower:
                location = city
                break

    # 3. Fallback to capitalized words that aren't qualities or dates (very basic)
    if not location:
        words = re.findall(r'\b[A-Z][a-z]+\b', query)
        for word in words:
            if word not in ["I", "Looking", "Find", "Searching"] and word not in DATES:
                location = word
                break

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
