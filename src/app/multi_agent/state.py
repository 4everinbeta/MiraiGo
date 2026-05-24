from __future__ import annotations

from copy import deepcopy
from typing import Any


DEFAULT_STATE: dict[str, Any] = {
    "user_intent": "",
    "trip_type": "other",
    "date_window": {
        "start": "",
        "end": "",
        "flexible_days": 0,
    },
    "trip_length_days": None,
    "origin": {
        "city": "",
        "airport": "",
    },
    "travelers": {
        "adults": 1,
        "children": 0,
        "child_ages": [],
    },
    "budget": {
        "currency": "USD",
        "min": None,
        "max": None,
        "comfort": "mid",
    },
    "preferences": {
        "climate": "",
        "pace": "balanced",
        "interests": [],
        "hotel_type": "hotel",
        "flight_constraints": [],
        "accessibility_needs": "",
    },
    "constraints": {
        "passport_ok": None,
        "max_flight_hours": None,
        "avoid": [],
    },
    "candidate_destinations": [],
    "quotes": {
        "retrieved_at": "",
        "currency": "USD",
        "packages": [],
    },
    "itineraries": [],
    "open_questions": [],
    "assumptions": [],
    "user_visible_disclaimers": [],
}


def new_state() -> dict[str, Any]:
    return deepcopy(DEFAULT_STATE)


def deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

