import re
import unicodedata
from datetime import date, timedelta
from typing import Any, Dict

from src.app.services.clarification import GLOBAL_CONFIDENCE_THRESHOLD
from src.app.schemas.search import ClarificationBudgetRange, TravelerCounts

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

MONTH_NAMES = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]

TIMELINE_TERMS = {
    *MONTH_NAMES,
    "summer",
    "winter",
    "spring",
    "fall",
    "next year",
    "next month",
    "early summer",
}


QUALITATIVE_BUDGET_MAP = {
    "cheap": (0, 1500),
    "budget": (0, 1500),
    "mid-range": (1500, 3500),
    "midrange": (1500, 3500),
    "luxury": (3500, 10000),
    "luxurious": (3500, 10000),
}

NORMALIZATION_REPLACEMENTS = {
    r"\bviaje\b": "trip",
    r"\bviajar\b": "travel",
    r"\bvacaciones\b": "vacation",
    r"\bpresupuesto\b": "budget",
    r"\bhasta\b": "up to",
    r"\bmaximo\b": "maximum",
    r"\beconomico\b": "budget",
    r"\bbarato\b": "cheap",
    r"\bbarata\b": "cheap",
    r"\blujoso\b": "luxurious",
    r"\bplaya\b": "beach",
    r"\bpraia\b": "beach",
    r"\bmontanas\b": "mountains",
    r"\bfamilia\b": "family friendly",
    r"\bcalido\b": "warm",
    r"\blluvia\b": "rain",
    r"\bsin lluvia\b": "no rain",
    r"\bsem chuva\b": "no rain",
    r"\bem\b": "in",
    r"\bcon\b": "with",
    r"\bdiciembre\b": "december",
    r"\benero\b": "january",
    r"\bfebrero\b": "february",
    r"\bmarzo\b": "march",
    r"\babril\b": "april",
    r"\bmayo\b": "may",
    r"\bjunio\b": "june",
    r"\bjulio\b": "july",
    r"\bagosto\b": "august",
    r"\bseptiembre\b": "september",
    r"\boctubre\b": "october",
    r"\bnoviembre\b": "november",
    r"\bdecembre\b": "december",
    r"\bjanvier\b": "january",
    r"\bfevrier\b": "february",
    r"\bmars\b": "march",
    r"\bavril\b": "april",
    r"\bjuin\b": "june",
    r"\bjuillet\b": "july",
    r"\baout\b": "august",
    r"\bseptembre\b": "september",
    r"\boctobre\b": "october",
    r"\bnovembre\b": "november",
}

QUALITY_SYNONYMS = {
    "beach": ["seaside", "coast", "coastal", "shore"],
    "mountains": ["alpine", "highlands", "peaks"],
    "family friendly": ["kid friendly", "family-focused", "child friendly"],
    "budget": ["affordable", "low cost", "value"],
    "luxurious": ["luxury", "upscale", "premium"],
    "romantic": ["honeymoon", "couples"],
    "hiking": ["trekking", "trail"],
}

UNCERTAINTY_MARKERS = ("maybe", "somewhere", "not sure", "perhaps", "roughly", "around")


LOCATION_STOP_TOKENS = {
    "for", "with", "that", "which", "who", "preferably", "prefer", "including", "includes",
}
LOCATION_TRAILING_STOP_TOKENS = LOCATION_STOP_TOKENS | {
    "from", "between", "and", "on", "next", "this", "my", "to", "in", "near", "at",
}
TO_VERB_TOKENS = {"find", "go", "travel", "plan", "book", "visit", "stay"}
ROUTE_CONTEXT_STOP_WORDS = (
    "for",
    "in",
    "on",
    "with",
    "between",
    "during",
    "around",
    "next",
    "this",
    "maybe",
    "sometime",
    "leaving",
    "departing",
)
NON_DESTINATION_TOKENS = {
    "budget",
    "cheap",
    "affordable",
    "moderate",
    "mid",
    "midrange",
    "mid-range",
    "luxury",
    "luxurious",
    "trip",
    "travel",
    "vacation",
    "holiday",
    "getaway",
    "flight",
    "flights",
    "stay",
    "stays",
    "hotel",
    "hotels",
    "accommodation",
    "accommodations",
}


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
        uncertain_timeline = _contains_uncertainty(query_lower)
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
            confidence=0.55 if uncertain_timeline else 0.72,
            ambiguous=uncertain_timeline,
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

    month_pattern = "|".join(MONTH_NAMES)
    month_range_match = re.search(
        rf"\b({month_pattern})\b\s+(?:or|and)\s+\b({month_pattern})\b",
        query_lower,
    )
    if month_range_match:
        start_month = month_range_match.group(1).title()
        end_month = month_range_match.group(2).title()
        source_text = month_range_match.group(0)
        normalized = {
            "window": {"start": start_month, "end": end_month},
            "precision": "month_range",
            "source_text": source_text,
        }
        return normalized, _build_slot_metadata(
            value=normalized,
            confidence=0.8,
            ambiguous=False,
            source_text=source_text,
        )

    if found_dates:
        first_date = found_dates[0]
        first_date_lower = first_date.lower()
        if first_date_lower in MONTH_NAMES:
            month_idx = MONTH_NAMES.index(first_date_lower) + 1
            today = date.today()
            year = today.year
            if month_idx < today.month:
                year += 1
            start_date = date(year, month_idx, 1)
            if month_idx == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month_idx + 1, 1) - timedelta(days=1)
            
            normalized = {
                "window": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "precision": "month",
                "source_text": first_date,
            }
            return normalized, _build_slot_metadata(
                value=normalized,
                confidence=0.8,
                ambiguous=False,
                source_text=first_date,
            )

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


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _normalize_query(query: str) -> str:
    normalized = _strip_accents(query).lower()
    for pattern, replacement in NORMALIZATION_REPLACEMENTS.items():
        normalized = re.sub(pattern, replacement, normalized)
    return normalized


def _contains_phrase(text: str, phrase: str) -> bool:
    escaped = re.escape(phrase).replace(r"\ ", r"\s+")
    return re.search(rf"\b{escaped}\b", text) is not None


def _contains_uncertainty(query_lower: str) -> bool:
    return any(token in query_lower for token in UNCERTAINTY_MARKERS)


def _extract_qualities(query_lower: str) -> list[str]:
    found: list[str] = []
    for quality in QUALITIES:
        if _contains_phrase(query_lower, quality):
            found.append(quality)

    for quality, synonyms in QUALITY_SYNONYMS.items():
        if quality in found:
            continue
        for synonym in synonyms:
            if _contains_phrase(query_lower, synonym):
                found.append(quality)
                break
    return found


def _extract_modes(query_lower: str) -> list[str]:
    found_modes = []
    for mode, keywords in MODES.items():
        for kw in keywords:
            if _contains_phrase(query_lower, kw):
                found_modes.append(mode)
                break
    return found_modes


def _extract_budget(query_lower: str) -> tuple[float | None, str | None, dict[str, Any] | None]:
    budget = None
    budget_source = None
    normalized_budget = None
    budget_match = re.search(r"(?:budget|max|maximum|up to)\s+(?:of\s+)?\$?(\d+)", query_lower)
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
        money_match = re.search(r"\$(\d+)", query_lower)
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
            if _contains_phrase(query_lower, phrase):
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
    return budget, budget_source, normalized_budget


def _extract_duration_days(query_lower: str) -> int | None:
    duration_match = re.search(
        r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+day",
        query_lower,
    )
    if not duration_match:
        return None
    val = duration_match.group(1)
    if val.isdigit():
        return int(val)
    return NUMBER_MAP.get(val)


def _looks_like_timeline_fragment(value: str) -> bool:
    lowered = value.lower()
    if any(month in lowered for month in MONTH_NAMES):
        return True
    if any(token in lowered for token in ["summer", "winter", "spring", "fall", "next month", "next year"]):
        return True
    if re.search(r"\b\d{1,2}(st|nd|rd|th)?\b", lowered):
        return True
    return False


def _normalize_location_candidate(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value).strip(" ,.")
    if len(normalized) == 3 and normalized.isalpha():
        return normalized.upper()
    return " ".join(token.capitalize() for token in normalized.split())


def _trim_location_fragment(value: str) -> str:
    trimmed = re.sub(
        rf"\s+\b(?:{'|'.join(ROUTE_CONTEXT_STOP_WORDS)})\b.*$",
        "",
        value,
        flags=re.IGNORECASE,
    )
    return trimmed.strip(" ,.")


def _is_destination_candidate(value: str) -> bool:
    candidate = value.strip(" ,.")
    lowered = candidate.lower()
    if not candidate:
        return False
    tokenized = {token for token in re.split(r"[\s-]+", lowered) if token}
    if "budget" in tokenized:
        return False
    if tokenized and tokenized.issubset(NON_DESTINATION_TOKENS):
        return False
    if lowered in TIMELINE_TERMS:
        return False
    if _looks_like_timeline_fragment(candidate):
        return False
    return True


def _extract_destination(query: str, query_lower: str, origin_hint: str | None = None) -> str | None:
    route_hints = extract_route_hints(query)
    if route_hints["destination"]:
        return route_hints["destination"]

    def is_invalid_destination(candidate: str) -> bool:
        candidate_lower = candidate.lower()
        if origin_hint and candidate_lower in origin_hint.lower():
            return True
        pattern = (
            r'\bfrom\s+(?:[a-z\s.-]{0,15}\s+)?'
            + re.escape(candidate_lower)
            + r'\b'
        )
        if re.search(pattern, query_lower):
            return True
        return False

    route_match = re.search(
        r"\bfrom\b\s+([A-Za-z][A-Za-z\s.-]*?)\s+\bto\b\s+([A-Za-z][A-Za-z\s.-]*?)(?:\s+\b(?:for|in|on|with|between|during|and|con)\b|$)",
        query,
        re.IGNORECASE,
    )
    if route_match:
        destination_candidate = route_match.group(2).strip()
        if _is_destination_candidate(destination_candidate):
            return _normalize_location_candidate(destination_candidate)

    route_match_alt = re.search(
        r"\bde\b\s+([A-Za-z][A-Za-z\s.-]*?)\s+\ba\b\s+([A-Za-z][A-Za-z\s.-]*?)(?:\s+\b(?:for|in|on|with|between|during|para|en|con|and)\b|$)",
        query,
        re.IGNORECASE,
    )
    if route_match_alt:
        destination_candidate = route_match_alt.group(2).strip()
        if _is_destination_candidate(destination_candidate):
            return _normalize_location_candidate(destination_candidate)

    voyage_pattern = re.search(
        r"\b(?:voyage|trip|viaje|viagem)\b(?:\s+[A-Za-z]+){0,4}\s+\ba\b\s+([A-Za-z][A-Za-z\s.-]*?)(?:\s+\b(?:from|for|with|between|on|during|next|this|in|en|and|con)\b|$)",
        query,
        re.IGNORECASE,
    )
    if voyage_pattern:
        destination_candidate = voyage_pattern.group(1).strip()
        if _is_destination_candidate(destination_candidate):
            return _normalize_location_candidate(destination_candidate)

    preposition_patterns = (
        r"\b(?:to|near|at|para)\b\s+([A-Za-z][A-Za-z\s.-]*?)(?:\s+\b(?:from|for|with|between|on|during|next|this|in|en|and|con)\b|$)",
        r"\b(?:in|en)\b\s+([A-Za-z][A-Za-z\s.-]*?)(?:\s+\b(?:from|for|with|between|on|during|next|this|para|and|con)\b|$)",
    )
    for pattern in preposition_patterns:
        for location_match in re.finditer(pattern, query, re.IGNORECASE):
            destination_candidate = location_match.group(1).strip()
            if _is_destination_candidate(destination_candidate):
                return _normalize_location_candidate(destination_candidate)

    for city in COMMON_CITIES:
        if city.lower() in query_lower:
            if is_invalid_destination(city):
                continue
            return city

    words = re.findall(r'\b[A-Z][a-z]+\b', query)
    stop_words = {
        "I", "Looking", "Find", "Searching", "Need", "Plan", "Trip", "Help",
        "Flight", "Flights", "Stay", "Stays", "Hotel", "Hotels",
        "Accommodation", "Accommodations", "Vacation", "Vacations"
    }
    for word in words:
        if word not in stop_words and word not in DATES and _is_destination_candidate(word):
            if is_invalid_destination(word):
                continue
            return word

    return None


def extract_intent(query: str) -> Dict[str, Any]:
    query_lower = _normalize_query(query)
    normalized_query = _strip_accents(query)
    route_hints = extract_route_hints(normalized_query)
    location = (
        route_hints["destination"]
        or _extract_destination(
            normalized_query, query_lower, route_hints["origin"]
        )
    )

    # Qualities Extraction
    found_qualities = _extract_qualities(query_lower)
            
    # Dates Extraction
    found_dates = []
    for date in DATES:
        if _contains_phrase(query_lower, date.lower()):
            found_dates.append(date)

    # Date Range Extraction
    date_range = None
    stop_keywords = r'with|in|near|at|searching|looking|for'
    
    from_to_match = re.search(fr'from\s+(.+?)\s+to\s+(.+?)(?:\s+(?:{stop_keywords})|$)', query, re.IGNORECASE)
    if from_to_match:
        start_text = from_to_match.group(1).strip()
        end_text = from_to_match.group(2).strip()
        if _looks_like_timeline_fragment(start_text) and _looks_like_timeline_fragment(end_text):
            date_range = {"start": start_text, "end": end_text}
    else:
        between_and_match = re.search(fr'between\s+(.+?)\s+and\s+(.+?)(?:\s+(?:{stop_keywords})|$)', query, re.IGNORECASE)
        if between_and_match:
            start_text = between_and_match.group(1).strip()
            end_text = between_and_match.group(2).strip()
            if _looks_like_timeline_fragment(start_text) and _looks_like_timeline_fragment(end_text):
                date_range = {
                    "start": start_text,
                    "end": end_text
                }

    # Modes Extraction
    found_modes = _extract_modes(query_lower)

    # Budget Extraction
    budget, budget_source, normalized_budget = _extract_budget(query_lower)

    # Duration Extraction
    duration_days = _extract_duration_days(query_lower)
    normalized_timeline, timeline_metadata = _extract_timeline(query_lower, date_range, found_dates)
    normalized_weather, weather_metadata = _extract_weather(query_lower)

    destination_source = location
    destination_ambiguous = False
    destination_confidence = 0.0
    if location:
        destination_confidence = 0.9
        if _contains_uncertainty(query_lower):
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

    # Travelers count extraction
    travelers = extract_party_size(query)

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
        "origin_hint": route_hints["origin"],
        "original_query": query,
        "travelers": travelers,
    }


def extract_route_hints(query: str) -> dict[str, str | None]:
    route_match = re.search(
        r"\bfrom\b\s+([A-Za-z][A-Za-z\s.'-]*?)\s+\bto\b\s+([A-Za-z][A-Za-z\s.'-]*?)(?:$|\s+\b(?:for|in|on|with|between|during|around|next|this|maybe|sometime|leaving|departing)\b)",
        query,
        re.IGNORECASE,
    )
    if route_match:
        origin_candidate = _trim_location_fragment(route_match.group(1))
        destination_candidate = _trim_location_fragment(route_match.group(2))
        origin = (
            _normalize_location_candidate(origin_candidate)
            if _is_destination_candidate(origin_candidate)
            else None
        )
        destination = (
            _normalize_location_candidate(destination_candidate)
            if _is_destination_candidate(destination_candidate)
            else None
        )
        return {"origin": origin, "destination": destination}

    reverse_route_match = re.search(
        r"\bto\b\s+([A-Za-z][A-Za-z\s.'-]*?)\s+\bfrom\b\s+([A-Za-z][A-Za-z\s.'-]*?)(?:$|\s+\b(?:for|in|on|with|between|during|around|next|this|maybe|sometime|leaving|departing)\b)",
        query,
        re.IGNORECASE,
    )
    if reverse_route_match:
        destination_candidate = _trim_location_fragment(reverse_route_match.group(1))
        origin_candidate = _trim_location_fragment(reverse_route_match.group(2))
        origin = (
            _normalize_location_candidate(origin_candidate)
            if _is_destination_candidate(origin_candidate)
            else None
        )
        destination = (
            _normalize_location_candidate(destination_candidate)
            if _is_destination_candidate(destination_candidate)
            else None
        )
        return {"origin": origin, "destination": destination}

    # Standalone origin match (from <location>)
    standalone_pattern = (
        r"\bfrom\b\s+([A-Za-z][A-Za-z\s.'-]*?)"
        r"(?:$|\s+\b(?:for|in|on|with|between|during|around|next|this|"
        r"maybe|sometime|leaving|departing|to)\b)"
    )
    standalone_origin_match = re.search(
        standalone_pattern,
        query,
        re.IGNORECASE,
    )
    if standalone_origin_match:
        origin_candidate = _trim_location_fragment(standalone_origin_match.group(1))
        origin = (
            _normalize_location_candidate(origin_candidate)
            if _is_destination_candidate(origin_candidate)
            else None
        )
        return {"origin": origin, "destination": None}

    return {"origin": None, "destination": None}


# ---------------------------------------------------------------------------
# Itinerary-specific extraction helpers
# ---------------------------------------------------------------------------

def extract_party_size(text: str) -> TravelerCounts | None:
    """Parse party-size descriptions like "family of three", "couple", "two adults one child"."""
    text_lower = text.lower()

    # "family of X" — default to 2 adults + (X-2) children
    family_match = re.search(r"family of (\w+)", text_lower)
    if family_match:
        raw = family_match.group(1)
        total = NUMBER_MAP.get(raw) or (int(raw) if raw.isdigit() else None)
        if total and total >= 2:
            children = max(0, total - 2)
            return TravelerCounts(adults=2, children=children)

    # "couple" → 2 adults
    if re.search(r"\bcouple\b", text_lower):
        return TravelerCounts(adults=2, children=0)

    # "solo" → 1 adult
    if re.search(r"\bsolo\b|\bjust me\b|\bby myself\b", text_lower):
        return TravelerCounts(adults=1, children=0)

    # "X adults Y children" or "X adults and Y kids"
    explicit_match = re.search(
        r"(\w+)\s+adults?\s+(?:and\s+)?(\w+)\s+(?:children|kids?|child)",
        text_lower,
    )
    if explicit_match:
        raw_adults = explicit_match.group(1)
        raw_children = explicit_match.group(2)
        adults = NUMBER_MAP.get(raw_adults) or (int(raw_adults) if raw_adults.isdigit() else None)
        children = NUMBER_MAP.get(raw_children) or (int(raw_children) if raw_children.isdigit() else None)
        if adults:
            return TravelerCounts(adults=adults, children=children or 0)

    # "X adults"
    adults_only_match = re.search(r"(\w+)\s+adults?", text_lower)
    if adults_only_match:
        raw = adults_only_match.group(1)
        adults = NUMBER_MAP.get(raw) or (int(raw) if raw.isdigit() else None)
        if adults:
            return TravelerCounts(adults=adults, children=0)

    return None


def extract_budget_range(text: str) -> ClarificationBudgetRange | None:
    """Parse budget expressions like "$6000-$7500", "$6000 to $7500", "between $6000 and $7500"."""

    def _clean_num(s: str) -> float | None:
        cleaned = re.sub(r"[,$\s]", "", s)
        try:
            return float(cleaned)
        except ValueError:
            return None

    # "$X-$Y" or "$X - $Y"
    range_match = re.search(
        r"\$?([\d,]+)\s*[-–]\s*\$?([\d,]+)",
        text,
    )
    if range_match:
        lo = _clean_num(range_match.group(1))
        hi = _clean_num(range_match.group(2))
        if lo is not None and hi is not None:
            return ClarificationBudgetRange(minimum=lo, maximum=hi)

    # "$X to $Y" or "between $X and $Y"
    to_match = re.search(
        r"(?:between\s+)?\$?([\d,]+)\s+(?:to|and)\s+\$?([\d,]+)",
        text,
        re.IGNORECASE,
    )
    if to_match:
        lo = _clean_num(to_match.group(1))
        hi = _clean_num(to_match.group(2))
        if lo is not None and hi is not None:
            return ClarificationBudgetRange(minimum=lo, maximum=hi)

    # "up to $X" or "under $X"
    upper_match = re.search(r"(?:up to|under|below|max(?:imum)?)\s+\$?([\d,]+)", text, re.IGNORECASE)
    if upper_match:
        hi = _clean_num(upper_match.group(1))
        if hi is not None:
            return ClarificationBudgetRange(minimum=None, maximum=hi)

    return None


def extract_candidate_destinations(text: str) -> list[str]:
    """Extract destination candidates listed after signal phrases like 'like', 'including', 'such as'."""
    signal_phrases = (
        r"(?:like|including|such as|consider|places? like|destinations? like|options? like|"
        r"areas? like|regions? like|spots? like)"
    )
    match = re.search(signal_phrases + r"\s+(.+?)(?:\?|$)", text, re.IGNORECASE)
    if not match:
        return []

    raw = match.group(1).strip()
    # Split on ", ", " or ", " and "
    parts = re.split(r",\s*|\s+or\s+|\s+and\s+", raw, flags=re.IGNORECASE)
    # Strip leading conjunctions and articles left by comma-first splitting
    candidates = []
    for p in parts:
        cleaned = p.strip().rstrip("?.,;")
        cleaned = re.sub(r"^(?:or|and)\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^the\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        if cleaned:
            candidates.append(cleaned)
    return candidates
