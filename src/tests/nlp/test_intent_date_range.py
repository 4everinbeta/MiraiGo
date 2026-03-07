from src.app.nlp.intent import extract_intent

def test_extract_intent_date_range_from_to():
    query = "Trip to Paris from December 1st to December 15th"
    intent = extract_intent(query)
    assert intent["location"] == "Paris"
    assert intent["date_range"] == {"start": "December 1st", "end": "December 15th"}

def test_extract_intent_date_range_between():
    query = "Looking for a beach stay between July and August in Miami"
    intent = extract_intent(query)
    assert intent["location"] == "Miami"
    assert "beach" in intent["qualities"]
    assert intent["date_range"] == {"start": "July", "end": "August"}
