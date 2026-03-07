from src.app.nlp.intent import extract_intent

def test_extract_intent_multimodal_car():
    query = "Search for a flight and car rental in London"
    intent = extract_intent(query)
    assert intent["location"] == "London"
    assert "car" in intent["modes"]

def test_extract_intent_multimodal_bundle():
    query = "Looking for a flight + hotel bundle to Tokyo"
    intent = extract_intent(query)
    assert intent["location"] == "Tokyo"
    assert "bundle" in intent["modes"]

def test_extract_intent_multimodal_stay_only():
    query = "Just a stay in Paris"
    intent = extract_intent(query)
    assert intent["location"] == "Paris"
    assert "stay" in intent["modes"]
    assert "car" not in intent["modes"]
