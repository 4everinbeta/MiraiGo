from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_cors_headers():
    # Simulate an OPTIONS request from the frontend origin
    response = client.options(
        "/api/v1/search",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        }
    )
    # If CORS is NOT configured, this will either return 405 (if OPTIONS is not handled)
    # or it will return 200 but WITHOUT the CORS headers.
    # CORSMiddleware handles OPTIONS and returns 200 with headers.
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response.headers.get("access-control-allow-credentials") == "true"
