import httpx
import asyncio

async def verify():
    # We'll use the running app (if started via docker compose) or mock it.
    # For this verification, we'll try to hit the local uvicorn if it's running.
    url = "http://localhost:8001/api/v1/search"
    query = "Find a luxurious beach trip in Miami"
    print(f"Testing API with query: {query}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params={"q": query}, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                print(f"API Response Success!")
                print(f"Location: {data['intent']['location']}")
                print(f"Qualities: {data['intent']['qualities']}")
                print(f"Results Count: {data['count']}")
                for i, res in enumerate(data['results'][:3]):
                    print(f"{i+1}. {res['provider']} (Score: {res['score']}): {res['text']}")
            else:
                print(f"API Error: {response.status_code}")
                print(response.text)
    except Exception as e:
        print(f"Could not reach API: {e}. (Ensure server is running with 'uvicorn src.app.main:app')")

if __name__ == "__main__":
    asyncio.run(verify())
