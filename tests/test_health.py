"""Health endpoint smoke test."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    """GET /health responds with HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
