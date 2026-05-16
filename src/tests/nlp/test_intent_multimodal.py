from src.app.nlp.intent import extract_intent


def test_portuguese_like_prompt_normalizes_weather_budget_and_month():
    intent = extract_intent("Procuro viagem barata para praia em agosto sem chuva")

    assert "August" in intent["dates"]
    assert intent["normalized_budget"]["category"] == "cheap"
    assert intent["normalized_weather"]["precipitation"] == "avoid_rain"
    assert "beach" in intent["qualities"]


def test_french_month_token_keeps_destination_parsing():
    intent = extract_intent("Je veux un voyage a lisbonne en novembre")

    assert intent["location"] == "Lisbonne"
    assert "November" in intent["dates"]


def test_spanish_style_viaje_a_destination_pattern_is_supported():
    intent = extract_intent("Quiero un viaje economico a lisboa en julio")

    assert intent["location"] == "Lisboa"
    assert "July" in intent["dates"]
