from src.app.nlp.intent import extract_intent

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
