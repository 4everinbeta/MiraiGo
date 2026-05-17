import re
from datetime import date, timedelta
from typing import Any, Dict

from src.app.services.clarification import GLOBAL_CONFIDENCE_THRESHOLD

QUALITIES = [
    "warm", "beach", "mountains", "mountain", "amusement parks", "family friendly",
    "luxurious", "budget", "romantic", "quiet", "hiking", "skiing"
]

DATES = [
    "December", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November",
    "summer", "winter", "spring", "fall", "next year", "next month"
]
DATE_TERMS_LOWER = {token.lower() for token in DATES}

MODES = {
    "flight": ["flight", "plane", "flying"],
    "stay": ["stay", "hotel", "accommodation", "resort", "airbnb", "hostel", "apartment"],
    "car": ["car", "rental", "driving", "vehicle"],
    "bundle": ["bundle", "package", "all-in-one", "+"]
}

# Common cities for better extraction
COMMON_CITIES = [
    "Paris", "London", "Tokyo", "New York", "Miami", "Denver", "Rome", "Barcelona", "Berlin", "Dubai", "Lisboa"
]

NUMBER_MAP = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}


QUALITATIVE_BUDGET_MAP = {
    "cheap": (0, 1500),
    "budget": (0, 1500),
    "mid-range": (1500, 3500),
    "midrange": (1500, 3500),
    "luxury": (3500, 10000),
    "luxurious": (3500, 10000),
}


LOCATION_STOP_TOKENS = {
    "for", "with", "that", "which", "who", "preferably", "prefer", "including", "includes",
}
LOCATION_TRAILING_STOP_TOKENS = LOCATION_STOP_TOKENS | {
    "from", "between", "and", "on", "next", "this", "my", "to", "in", "near", "at",
}
TO_VERB_TOKENS = {"find", "go", "travel", "plan", "book", "visit", "stay"}


def _normalize_location_name(raw_location: str) -> str:
    cleaned = raw_location.strip(" ,.;:!?")
    if not cleaned:
        return cleaned
    tokens = []
    for token in cleaned.split():
        if len(token) <= 3 and token.isupper():
            tokens.append(token)
        else:
            tokens.append(token.capitalize())
    return " ".join(tokens)


def _extract_location_phrase(query: str) -> str | None:
    for match in re.finditer(
        r"\b(to|in|near|at)\b\s+([A-Za-z][A-Za-z'\-]*(?:\s+[A-Za-z][A-Za-z'\-]*){0,5})",
        query,
        re.IGNORECASE,
    ):
        preposition = match.group(1).lower()
        raw_location = match.group(2).strip()
        if not raw_location:
            continue
        candidate_tokens = raw_location.split()
        while candidate_tokens and candidate_tokens[0].lower() in {"the", "a", "an"}:
            candidate_tokens = candidate_tokens[1:]
        if not candidate_tokens:
            continue
        if preposition == "to" and candidate_tokens[0].lower() in TO_VERB_TOKENS:
            continue
        trimmed_tokens: list[str] = []
        for token in candidate_tokens:
            token_lower = token.lower()
            if token_lower in LOCATION_TRAILING_STOP_TOKENS:
                break
            trimmed_tokens.append(token)
        if not trimmed_tokens:
            continue
        candidate_tokens = trimmed_tokens
        first_token = candidate_tokens[0].lower()
        if first_token in LOCATION_STOP_TOKENS or first_token in DATE_TERMS_LOWER:
            continue
        return _normalize_location_name(" ".join(candidate_tokens))
    return None


def _build_slot_metadata(
    *,
    value: Any,
    confidence: float,
    ambiguous: bool,
    source_text: str | None,
) -> dict[str, Any]:
    return {
        "value": value,
        "confidence": max(0.0, min(1.0, confidence)),
        "ambiguous": ambiguous,
        "source_text": source_text,
    }


def _next_month_window() -> tuple[date, date]:
    today = date.today()
    month = today.month + 1
    year = today.year
    if month == 13:
        month = 1
        year += 1
    start = date(year, month, 1)

    after_next_month = month + 1
    after_next_year = year
    if after_next_month == 13:
        after_next_month = 1
        after_next_year += 1
    end = date(after_next_year, after_next_month, 1) - timedelta(days=1)
    return start, end


def _extract_timeline(query_lower: str, date_range: dict[str, str] | None, found_dates: list[str]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if date_range:
        normalized = {
            "window": {
                "start": date_range.get("start"),
                "end": date_range.get("end"),
            },
            "precision": "range",
            "source_text": f"{date_range.get('start')} to {date_range.get('end')}",
        }
        return normalized, _build_slot_metadata(
            value=normalized,
            confidence=0.95,
            ambiguous=False,
            source_text=normalized["source_text"],
        )

    early_summer_match = re.search(r"early summer", query_lower)
    if early_summer_match:
        year = date.today().year
        normalized = {
            "window": {
                "start": date(year, 6, 1).isoformat(),
                "end": date(year, 7, 15).isoformat(),
            },
            "precision": "season_part",
            "source_text": "early summer",
        }
        return normalized, _build_slot_metadata(
            value=normalized,
            confidence=0.55,
            ambiguous=False,
            source_text="early summer",
        )

    if "next month" in query_lower:
        start, end = _next_month_window()
        normalized = {
            "window": {"start": start.isoformat(), "end": end.isoformat()},
            "precision": "month",
            "source_text": "next month",
        }
        return normalized, _build_slot_metadata(
            value=normalized,
            confidence=0.7,
            ambiguous=False,
            source_text="next month",
        )

    if found_dates:
        first_date = found_dates[0]
        normalized = {
            "window": {"start": first_date, "end": None},
            "precision": "text",
            "source_text": first_date,
        }
        return normalized, _build_slot_metadata(
            value=normalized,
            confidence=0.7,
            ambiguous=False,
            source_text=first_date,
        )

    return None, _build_slot_metadata(
        value=None,
        confidence=0.0,
        ambiguous=True,
        source_text=None,
    )


def _extract_weather(query_lower: str) -> tuple[dict[str, str] | None, dict[str, Any]]:
    weather = {}
    source_text = None
    confidence = 0.0
    ambiguous = False

    if "warm weather" in query_lower or "warm" in query_lower:
        weather["temperature"] = "warm"
        source_text = "warm weather" if "warm weather" in query_lower else "warm"
        confidence = 0.85
    elif "cool weather" in query_lower or "cool" in query_lower:
        weather["temperature"] = "cool"
        source_text = "cool weather" if "cool weather" in query_lower else "cool"
        confidence = 0.85

    if "avoid rain" in query_lower or "no rain" in query_lower:
        weather["precipitation"] = "avoid_rain"
        source_text = "avoid rain" if "avoid rain" in query_lower else "no rain"
        confidence = max(confidence, 0.9)
    elif "rain" in query_lower and "avoid" not in query_lower:
        weather["precipitation"] = "rain_ok"
        source_text = "rain"
        confidence = max(confidence, 0.55)
        ambiguous = True

    if "nice weather" in query_lower:
        weather["temperature"] = "pleasant"
        source_text = "nice weather"
        confidence = 0.45
        ambiguous = True

    normalized = weather or None
    metadata = _build_slot_metadata(
        value=normalized,
        confidence=confidence,
        ambiguous=ambiguous or normalized is None,
        source_text=source_text,
    )
    return normalized, metadata


def extract_intent(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    # 1. Try explicit location keywords (to|in|near|at)
    location = _extract_location_phrase(query)
    
    # 2. If no explicit match, try finding common cities directly
    if not location:
        for city in COMMON_CITIES:
            if city.lower() in query_lower:
                location = city
                break

    # 3. Fallback to capitalized words that aren't qualities or dates (very basic)
    if not location:
        words = re.findall(r'\b[A-Z][a-z]+\b', query)
        stop_words = {"I", "Looking", "Find", "Searching", "Need", "Plan", "Trip", "Help"}
        for word in words:
            if word not in stop_words and word not in DATES:
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
    stop_keywords = r'with|in|near|at|searching|looking|for'
    
    from_to_match = re.search(fr'from\s+(.+?)\s+to\s+(.+?)(?:\s+(?:{stop_keywords})|$)', query, re.IGNORECASE)
    if from_to_match:
        date_range = {
            "start": from_to_match.group(1).strip(),
            "end": from_to_match.group(2).strip()
        }
    else:
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

    # Budget Extraction
    budget = None
    budget_source = None
    normalized_budget = None
    budget_match = re.search(r'(?:budget|max|maximum|up to)\s+(?:of\s+)?\$?(\d+)', query_lower)
    if budget_match:
        budget = float(budget_match.group(1))
        budget_source = budget_match.group(0)
        normalized_budget = {
            "minimum": 0,
            "maximum": budget,
            "category": "numeric_cap",
            "source_text": budget_source,
        }
    elif "$" in query_lower:
        money_match = re.search(r'\$(\d+)', query_lower)
        if money_match:
            budget = float(money_match.group(1))
            budget_source = money_match.group(0)
            normalized_budget = {
                "minimum": 0,
                "maximum": budget,
                "category": "numeric_cap",
                "source_text": budget_source,
            }
    if normalized_budget is None:
        for phrase, (minimum, maximum) in QUALITATIVE_BUDGET_MAP.items():
            if phrase in query_lower:
                category = "mid-range" if phrase in {"mid-range", "midrange"} else phrase
                normalized_budget = {
                    "minimum": minimum,
                    "maximum": maximum,
                    "category": category,
                    "source_text": phrase,
                }
                budget = float(maximum)
                budget_source = phrase
                break

    # Duration Extraction
    duration_days = None
    duration_match = re.search(r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+day', query_lower)
    if duration_match:
        val = duration_match.group(1)
        if val.isdigit():
            duration_days = int(val)
        else:
            duration_days = NUMBER_MAP.get(val)
    normalized_timeline, timeline_metadata = _extract_timeline(query_lower, date_range, found_dates)
    normalized_weather, weather_metadata = _extract_weather(query_lower)

    destination_source = location
    destination_ambiguous = False
    destination_confidence = 0.0
    if location:
        destination_confidence = 0.9
        if any(token in query_lower for token in ["maybe", "somewhere", "not sure"]):
            destination_confidence = 0.45
            destination_ambiguous = True
    else:
        destination_ambiguous = True

    trip_length_metadata = _build_slot_metadata(
        value=duration_days,
        confidence=0.9 if duration_days else 0.0,
        ambiguous=duration_days is None,
        source_text=f"{duration_days} day" if duration_days else None,
    )

    budget_metadata = _build_slot_metadata(
        value=normalized_budget,
        confidence=0.9 if normalized_budget else 0.0,
        ambiguous=normalized_budget is None,
        source_text=budget_source,
    )

    slot_metadata = {
        "destination": _build_slot_metadata(
            value=location,
            confidence=destination_confidence,
            ambiguous=destination_ambiguous,
            source_text=destination_source,
        ),
        "timeline": timeline_metadata,
        "trip_length": trip_length_metadata,
        "budget": budget_metadata,
        "weather": weather_metadata,
    }

    return {
        "location": location,
        "qualities": found_qualities,
        "dates": found_dates,
        "date_range": date_range,
        "modes": found_modes,
        "budget": budget,
        "duration_days": duration_days,
        "normalized_timeline": normalized_timeline,
        "normalized_budget": normalized_budget,
        "normalized_weather": normalized_weather,
        "weather_follow_up_eligible": (
            weather_metadata["ambiguous"]
            or weather_metadata["confidence"] < GLOBAL_CONFIDENCE_THRESHOLD
        ),
        "slot_metadata": slot_metadata,
        "original_query": query,
    }
