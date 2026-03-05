from src.app.nlp.intent import extract_intent
from src.app.optimization.engine import rank_results

def verify():
    query = "I want a luxurious beach holiday in Miami next summer"
    print(f"Query: {query}")
    
    intent = extract_intent(query)
    print(f"Extracted Intent: {intent}")
    
    results = [
        {"provider": "Expedia", "text": "Basic beach room", "price": 200},
        {"provider": "Booking.com", "text": "Luxurious oceanfront suite", "price": 1000},
        {"provider": "Airbnb", "text": "Cozy mountain cabin", "price": 150}
    ]
    
    ranked = rank_results(results, intent["qualities"])
    print("\nRanked Results:")
    for i, res in enumerate(ranked):
        print(f"{i+1}. {res['provider']} (Score: {res['score']}): {res['text']}")

if __name__ == "__main__":
    verify()
