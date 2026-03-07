import re
from typing import Dict, List, Any, Optional

QUALITIES = [
    "warm", "beach", "mountains", "mountain", "amusement parks", "family friendly",
    "luxurious", "budget", "romantic", "quiet", "hiking", "skiing"
]

DATES = [
    "December", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November",
    "summer", "winter", "spring", "fall", "next year", "next month"
]

MODES = {
    "flight": ["flight", "plane", "flying"],
    "stay": ["stay", "hotel", "accommodation", "resort", "airbnb", "hostel", "apartment"],
    "car": ["car", "rental", "driving", "vehicle"],
    "bundle": ["bundle", "package", "all-in-one", "+"]
}

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

    # Date Range Extraction
    date_range = None
    # from [start] to [end]
    stop_keywords = r'with|in|near|at|searching|looking|for'
    
    from_to_match = re.search(fr'from\s+(.+?)\s+to\s+(.+?)(?:\s+(?:{stop_keywords})|$)', query, re.IGNORECASE)
    if from_to_match:
        date_range = {
            "start": from_to_match.group(1).strip(),
            "end": from_to_match.group(2).strip()
        }
    else:
        # between [start] and [end]
        between_and_match = re.search(fr'between\s+(.+?)\s+and\s+(.+?)(?:\s+(?:{stop_keywords})|$)', query, re.IGNORECASE)
        if between_and_match:
            date_range = {
                "start": between_and_match.group(1).strip(),
                "end": between_and_match.group(2).strip()
            }

    # Modes Extraction
    found_modes = []
    for mode, keywords in MODES.items():
        for kw in keywords:
            if kw in query_lower:
                found_modes.append(mode)
                break
            
    return {
        "location": location,
        "qualities": found_qualities,
        "dates": found_dates,
        "date_range": date_range,
        "modes": found_modes,
        "original_query": query
    }
