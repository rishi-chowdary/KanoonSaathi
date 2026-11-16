from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)


def test_public_health_does_not_require_auth():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-engine"
    assert "tesseract_available" in data


def test_internal_health_requires_key():
    response = client.get("/internal/health")
    # Missing header returns 422
    assert response.status_code in (401, 422)


def test_internal_health_rejects_wrong_key():
    response = client.get(
        "/internal/health",
        headers={"X-Internal-Api-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_internal_health_succeeds_with_valid_key():
    response = client.get(
        "/internal/health",
        headers={"X-Internal-Api-Key": settings.internal_api_key},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["provider"] == settings.llm_provider
