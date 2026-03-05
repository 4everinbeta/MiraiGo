from src.app.optimization.engine import rank_results

def test_rank_results_basic():
    results = [
        {"provider": "Expedia", "text": "Warm beach hotel", "price": 500},
        {"provider": "Booking.com", "text": "Mountain cabin", "price": 300},
        {"provider": "Airbnb", "text": "Sunny seaside villa", "price": 700}
    ]
    qualities = ["warm", "beach"]
    ranked = rank_results(results, qualities)
    # The first result matches both "warm" and "beach"
    # The third result matches "sunny" (near warm) and "seaside" (near beach)
    # The second result matches neither
    assert ranked[0]["provider"] == "Expedia"
    assert ranked[1]["provider"] == "Airbnb"
    assert ranked[2]["provider"] == "Booking.com"
