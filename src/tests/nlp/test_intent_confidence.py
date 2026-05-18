from datetime import date, timedelta

from src.app.services.clarification import GLOBAL_CONFIDENCE_THRESHOLD
from src.app.nlp.intent import extract_intent


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


def test_ambiguous_destination_and_timeline_are_marked_low_confidence():
    intent = extract_intent("maybe somewhere warm, not sure where, maybe early summer")
    destination = intent["slot_metadata"]["destination"]
    timeline = intent["slot_metadata"]["timeline"]

    assert destination["ambiguous"] is True
    assert destination["confidence"] < GLOBAL_CONFIDENCE_THRESHOLD
    assert timeline["ambiguous"] is True
    assert timeline["confidence"] < GLOBAL_CONFIDENCE_THRESHOLD


def test_flexible_timeline_phrases_normalize_to_window_with_precision():
    intent_early_summer = extract_intent("I want to travel in early summer")
    timeline_early_summer = intent_early_summer["normalized_timeline"]
    assert timeline_early_summer["precision"] == "season_part"
    assert timeline_early_summer["window"]["start"].endswith("-06-01")
    assert timeline_early_summer["window"]["end"].endswith("-07-15")

    intent_next_month = extract_intent("Plan a trip next month")
    timeline_next_month = intent_next_month["normalized_timeline"]
    expected_start, expected_end = _next_month_window()
    assert timeline_next_month["precision"] == "month"
    assert timeline_next_month["window"]["start"] == expected_start.isoformat()
    assert timeline_next_month["window"]["end"] == expected_end.isoformat()


def test_qualitative_budget_terms_map_to_ranges_and_keep_source_text():
    cheap_intent = extract_intent("I want a cheap vacation")
    cheap_budget = cheap_intent["normalized_budget"]
    assert cheap_budget["category"] == "cheap"
    assert cheap_budget["minimum"] == 0
    assert cheap_budget["maximum"] == 1500
    assert cheap_budget["source_text"] == "cheap"

    midrange_intent = extract_intent("Looking for a mid-range getaway")
    midrange_budget = midrange_intent["normalized_budget"]
    assert midrange_budget["category"] == "mid-range"
    assert midrange_budget["minimum"] == 1500
    assert midrange_budget["maximum"] == 3500
    assert midrange_budget["source_text"] == "mid-range"


def test_weather_preferences_have_normalized_values_and_follow_up_eligibility():
    warm_weather_intent = extract_intent("Find warm weather with beach options")
    warm_weather = warm_weather_intent["normalized_weather"]
    assert warm_weather["temperature"] == "warm"
    assert warm_weather_intent["slot_metadata"]["weather"]["ambiguous"] is False
    assert warm_weather_intent["weather_follow_up_eligible"] is False

    avoid_rain_intent = extract_intent("I want to travel but avoid rain")
    avoid_rain = avoid_rain_intent["normalized_weather"]
    assert avoid_rain["precipitation"] == "avoid_rain"
    assert avoid_rain_intent["slot_metadata"]["weather"]["source_text"] == "avoid rain"

    uncertain_weather_intent = extract_intent("nice weather would be good")
    weather_slot = uncertain_weather_intent["slot_metadata"]["weather"]
    assert weather_slot["confidence"] < GLOBAL_CONFIDENCE_THRESHOLD
    assert weather_slot["ambiguous"] is True
    assert uncertain_weather_intent["weather_follow_up_eligible"] is True


def test_unsupported_language_pattern_stays_ambiguous_with_low_confidence():
    intent = extract_intent("旅行を計画したい")
    destination = intent["slot_metadata"]["destination"]
    timeline = intent["slot_metadata"]["timeline"]

    assert destination["value"] is None
    assert destination["ambiguous"] is True
    assert destination["confidence"] < GLOBAL_CONFIDENCE_THRESHOLD
    assert timeline["ambiguous"] is True
