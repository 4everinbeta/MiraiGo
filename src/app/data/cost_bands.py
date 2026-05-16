from __future__ import annotations

from typing import Any

from src.app.schemas.itinerary import ItineraryCostEstimate
from src.app.schemas.search import TravelerCounts

# Cost bands by region_key → season → component tuple (low_usd, high_usd)
# Season keys: "summer", "winter", "spring", "fall"
COST_BANDS: dict[str, dict[str, Any]] = {
    "vancouver-island": {
        "summer": {
            "flight_per_pax": (300, 700),
            "stay_per_night": (150, 400),
            "car_per_day": (60, 120),
            "car_needed": True,
        },
        "winter": {
            "flight_per_pax": (250, 600),
            "stay_per_night": (120, 320),
            "car_per_day": (55, 110),
            "car_needed": True,
        },
        "spring": {
            "flight_per_pax": (280, 650),
            "stay_per_night": (130, 360),
            "car_per_day": (58, 115),
            "car_needed": True,
        },
        "fall": {
            "flight_per_pax": (270, 640),
            "stay_per_night": (125, 350),
            "car_per_day": (57, 112),
            "car_needed": True,
        },
    },
    "new-england": {
        "summer": {
            "flight_per_pax": (150, 450),
            "stay_per_night": (120, 350),
            "car_per_day": (50, 100),
            "car_needed": True,
        },
        "winter": {
            "flight_per_pax": (130, 400),
            "stay_per_night": (90, 280),
            "car_per_day": (45, 90),
            "car_needed": True,
        },
        "spring": {
            "flight_per_pax": (140, 420),
            "stay_per_night": (100, 300),
            "car_per_day": (48, 95),
            "car_needed": True,
        },
        "fall": {
            "flight_per_pax": (160, 470),
            "stay_per_night": (130, 380),
            "car_per_day": (52, 105),
            "car_needed": True,
        },
    },
    "pacific-northwest": {
        "summer": {
            "flight_per_pax": (200, 500),
            "stay_per_night": (130, 350),
            "car_per_day": (55, 110),
            "car_needed": True,
        },
        "winter": {
            "flight_per_pax": (170, 450),
            "stay_per_night": (100, 280),
            "car_per_day": (50, 100),
            "car_needed": True,
        },
        "spring": {
            "flight_per_pax": (185, 470),
            "stay_per_night": (110, 300),
            "car_per_day": (52, 105),
            "car_needed": True,
        },
        "fall": {
            "flight_per_pax": (190, 480),
            "stay_per_night": (115, 310),
            "car_per_day": (53, 108),
            "car_needed": True,
        },
    },
}

_DEFAULT_SEASON = "summer"


def _midpoint(low: float, high: float) -> float:
    return (low + high) / 2.0


def estimate_cost(
    region_key: str,
    season: str,
    travelers: TravelerCounts,
    duration_nights: int,
    include_car: bool | None = None,
) -> ItineraryCostEstimate:
    """Return a midpoint-based cost estimate for a given region, season, and trip parameters."""
    bands = COST_BANDS.get(region_key, {})
    season_data = bands.get(season, bands.get(_DEFAULT_SEASON, {}))

    if not season_data:
        return ItineraryCostEstimate(
            total_estimated=0,
            flight_estimated=0,
            stay_estimated=0,
            car_estimated=0,
            confidence="low",
        )

    total_pax = travelers.adults + travelers.children
    flight_per_pax = _midpoint(*season_data["flight_per_pax"])
    flight_estimated = flight_per_pax * total_pax

    stay_per_night = _midpoint(*season_data["stay_per_night"])
    stay_estimated = stay_per_night * duration_nights

    car_needed = season_data.get("car_needed", False)
    if include_car is False:
        car_needed = False
    elif include_car is True:
        car_needed = True

    car_per_day = _midpoint(*season_data["car_per_day"]) if car_needed else 0.0
    car_estimated = car_per_day * duration_nights if car_needed else 0.0

    total_estimated = flight_estimated + stay_estimated + car_estimated

    return ItineraryCostEstimate(
        total_estimated=round(total_estimated, 2),
        flight_estimated=round(flight_estimated, 2),
        stay_estimated=round(stay_estimated, 2),
        car_estimated=round(car_estimated, 2),
        confidence="medium",
    )


def destination_to_region_key(destination: str) -> str | None:
    """Fuzzy-match a destination string to a known region key (lowercase substring match)."""
    destination_lower = destination.lower()
    for key in COST_BANDS:
        # Check if any word in the key appears in the destination
        key_words = key.replace("-", " ").split()
        if all(word in destination_lower for word in key_words):
            return key
        # Also check reverse: destination words in key
        dest_words = destination_lower.replace("-", " ").split()
        if any(word in key for word in dest_words if len(word) > 3):
            return key
    return None
