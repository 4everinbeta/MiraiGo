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


def test_extract_intent_handles_lowercase_destination_after_preposition():
    query = (
        "i would like to find a flight, car, and stay for july in england "
        "that includes stays in the cotswold's and cornwall"
    )
    intent = extract_intent(query)
    assert intent["location"] == "England"
