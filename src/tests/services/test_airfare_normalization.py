from src.app.services.airfare_normalization import normalize_airfare_offer


def test_equivalent_inputs_produce_stable_normalized_offer_id():
    first = normalize_airfare_offer(
        provider="amadeus",
        provider_offer_id="offer-1",
        origin_code="mia",
        destination_code="cdg",
        departure_at="2026-08-01T10:00:00Z",
        arrival_at="2026-08-01T18:00:00Z",
        total_price="1234.56",
        provider_currency="usd",
        requested_currency="USD",
        duration="PT8H",
        stops=0,
    )
    second = normalize_airfare_offer(
        provider="amadeus",
        provider_offer_id="offer-1",
        origin_code="MIA",
        destination_code="CDG",
        departure_at="2026-08-01T10:00:00Z",
        arrival_at="2026-08-01T18:00:00Z",
        total_price=1234.56,
        provider_currency="USD",
        requested_currency="USD",
        duration="PT8H",
        stops="0",
    )

    assert first["normalized_offer_id"] == second["normalized_offer_id"]
    assert first["missing_fields"] == []


def test_missing_values_emit_nulls_and_sorted_missing_fields():
    normalized = normalize_airfare_offer(
        provider="duffel",
        provider_offer_id=None,
        origin_code="SEA",
        destination_code="LIS",
        departure_at="",
        arrival_at=None,
        total_price=None,
        provider_currency=None,
        requested_currency="USD",
        duration=None,
        stops=None,
    )

    assert normalized["price_minor"] is None
    assert normalized["duration_minutes"] is None
    assert normalized["stops_count"] is None
    assert normalized["normalized_offer_id"] is None
    assert normalized["missing_fields"] == sorted(normalized["missing_fields"])
    assert normalized["missing_fields"] == [
        "arrival_at",
        "departure_at",
        "duration_minutes",
        "price_minor",
        "stops_count",
    ]


def test_currency_fallback_keeps_provider_currency_and_marks_conversion_status():
    normalized = normalize_airfare_offer(
        provider="duffel",
        provider_offer_id="duf-123",
        origin_code="SFO",
        destination_code="NRT",
        departure_at="2026-09-03T12:00:00Z",
        arrival_at="2026-09-04T02:00:00Z",
        total_price="550.20",
        provider_currency="EUR",
        requested_currency="USD",
        duration="PT14H",
        stops=1,
    )

    assert normalized["currency_code"] == "EUR"
    assert normalized["conversion_status"] == "unavailable"
