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


def test_extract_intent_month_or_month_timeline_range():
    query = (
        "I would like to plan a trip for my wife and son and I from Denver Colorado "
        "to somewhere warm and sunny in June or July for seven to ten days"
    )
    intent = extract_intent(query)

    assert intent["normalized_timeline"] is not None
    assert intent["normalized_timeline"]["window"] == {"start": "June", "end": "July"}
    assert intent["normalized_timeline"]["precision"] == "month_range"
    assert intent["slot_metadata"]["timeline"]["ambiguous"] is False


def test_extract_intent_from_to_route_does_not_create_date_range():
    query = "Plan flights from Denver to Miami for 7 days"
    intent = extract_intent(query)

    assert intent["date_range"] is None


def test_extract_intent_route_to_destination_with_lowercase_terms():
    query = "plan flights from denver to miami in june"
    intent = extract_intent(query)

    assert intent["location"] == "Miami"
    assert intent["date_range"] is None
