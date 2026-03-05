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
