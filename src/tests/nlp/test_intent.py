from src.app.nlp.intent import (
    extract_budget_range,
    extract_candidate_destinations,
    extract_intent,
    extract_party_size,
)

def test_extract_intent_basic():
    query = "Find a warm beach trip to Miami in December"
    intent = extract_intent(query)
    assert intent["location"] == "Miami"
    assert "warm" in intent["qualities"]
    assert "beach" in intent["qualities"]
    assert "December" in intent["dates"]

def test_extract_intent_complex():
    query = "Looking for family friendly mountains near Denver next summer"
    intent = extract_intent(query)
    assert intent["location"] == "Denver"
    assert "family friendly" in intent["qualities"]
    assert "mountains" in intent["qualities"]
    assert "summer" in intent["dates"]

def test_extract_intent_varied_phrasing():
    # Test different ways of specifying location and qualities
    query = "I want a luxurious stay in Tokyo for my honeymoon next month"
    intent = extract_intent(query)
    assert intent["location"] == "Tokyo"
    assert "luxurious" in intent["qualities"]
    assert "next month" in intent["dates"]

def test_extract_intent_implicit_location():
    # Location mentioned without 'to', 'in', or 'near'
    query = "Paris vacation with mountain views"
    intent = extract_intent(query)
    assert intent["location"] == "Paris"
    assert "mountain" in intent["qualities"]


def test_extract_intent_ignores_timeline_token_as_destination():
    query = "Need warm weather in June"
    intent = extract_intent(query)
    assert intent["location"] is None
    assert "June" in intent["dates"]


def test_extract_intent_accepts_lowercase_destination_after_preposition():
    query = "trip to lisbon in july"
    intent = extract_intent(query)
    assert intent["location"] == "Lisbon"


def test_extract_intent_supports_common_spanish_tokens():
    query = "Quiero un viaje economico para lisboa en julio"
    intent = extract_intent(query)
    assert intent["location"] == "Lisboa"
    assert intent["normalized_budget"]["category"] == "budget"
    assert "July" in intent["dates"]


def test_extract_intent_maps_synonyms_to_canonical_quality():
    query = "Need an affordable seaside getaway to porto"
    intent = extract_intent(query)
    assert "budget" in intent["qualities"]
    assert "beach" in intent["qualities"]


def test_extract_intent_does_not_treat_budget_phrase_as_destination():
    query = "I want a warm beach trip on a moderate budget"
    intent = extract_intent(query)
    assert intent["location"] is None
    assert intent["normalized_budget"] is not None
    assert intent["normalized_budget"]["category"] in {"mid-range", "budget"}


def test_extract_party_size_family_of_three():
    travelers = extract_party_size("Looking for a family of three trip")
    assert travelers is not None
    assert travelers.adults == 2
    assert travelers.children == 1


def test_extract_party_size_couple():
    travelers = extract_party_size("A couple looking for a summer trip")
    assert travelers is not None
    assert travelers.adults == 2
    assert travelers.children == 0


def test_extract_budget_range_dollar_dash():
    budget = extract_budget_range("Budget is $6000-$7500 total")
    assert budget is not None
    assert budget.minimum == 6000
    assert budget.maximum == 7500


def test_extract_budget_range_to_syntax():
    budget = extract_budget_range("Our target is $6,000 to $7,500")
    assert budget is not None
    assert budget.minimum == 6000
    assert budget.maximum == 7500


def test_extract_candidate_destinations_or_list():
    destinations = extract_candidate_destinations(
        "Considering places like Vancouver Island, New England, or Pacific Northwest"
    )
    assert len(destinations) == 3
    assert "Vancouver Island" in destinations
    assert "New England" in destinations
    assert "Pacific Northwest" in destinations


def test_extract_candidate_destinations_empty():
    destinations = extract_candidate_destinations("I want somewhere sunny this summer")
    assert destinations == []
