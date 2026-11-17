import os
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

# Ensure mock LLM is used for tests
os.environ["USE_MOCK_LLM"] = "true"

from app.main import app
from app.config import settings
from app.providers.mock_provider import MockProvider
from app.schemas.simplify import (
    GlossaryTerm,
    LLMSimplifyResult,
    SimplifyRequest,
    SimplifyResponse,
)
from app.services.clause_service import validate_numbers_and_dates
from app.services.simplify_service import simplify_text

client = TestClient(app)
VALID_HEADERS = {"X-Internal-Api-Key": settings.internal_api_key}


def test_simplify_request_validation():
    # Valid request
    req = SimplifyRequest(
        text="The Lessee shall indemnify the Lessor from all damages.",
        mode="simple_english",
    )
    assert req.mode == "simple_english"
    assert req.document_context is None

    # Invalid mode
    with pytest.raises(ValidationError):
        SimplifyRequest(
            text="Some legal text",
            mode="ultra_simple",  # type: ignore
        )

    # Empty text
    with pytest.raises(ValidationError):
        SimplifyRequest(text="")


@pytest.mark.anyio
async def test_simplify_text_with_mock_provider():
    provider = MockProvider()
    request = SimplifyRequest(
        text="The contractor shall indemnify and defend the company against all third-party losses caused by contractor negligence.",
        document_context="Master Services Agreement 2026",
        mode="simple_english",
    )

    response = await simplify_text(request, provider)
    assert isinstance(response, SimplifyResponse)
    assert response.mode == "simple_english"
    assert len(response.explanation) > 10
    assert len(response.glossary) == 2
    assert response.glossary[0].term == "Indemnify"
    assert len(response.what_could_be_missed) == 2
    assert response.is_grounded is True
    assert len(response.warnings) == 0


def test_validate_numbers_and_dates_invented_values():
    # Original text has no figures or dates
    original = "The contractor agrees to perform the services diligently."

    # Explanation with invented dollar amount and calendar month
    invented_explanation = {
        "simple_english": "The contractor must pay $50,000 before October and complete 15 tasks."
    }

    is_verified, warnings = validate_numbers_and_dates(original, invented_explanation)
    assert is_verified is False
    assert len(warnings) >= 2
    assert any("50,000" in w for w in warnings)
    assert any("october" in w.lower() for w in warnings)

    # Explanation with numbers present in original text
    legit_original = "The tenant shall pay $2,500 on the 1st day of each month with a 15-day grace period."
    legit_explanation = {
        "detailed": "Tenant owes $2,500 monthly on the 1st day with 15-day grace."
    }
    is_legit, legit_warnings = validate_numbers_and_dates(legit_original, legit_explanation)
    assert is_legit is True
    assert len(legit_warnings) == 0


def test_internal_simplify_endpoint_auth():
    payload = {
        "text": "The party shall indemnify and hold harmless the other party.",
        "mode": "detailed",
    }

    # 1. Missing API key
    res_no_key = client.post("/internal/simplify", json=payload)
    assert res_no_key.status_code == 401

    # 2. Invalid API key
    res_bad_key = client.post(
        "/internal/simplify",
        headers={"X-Internal-Api-Key": "wrong_key"},
        json=payload,
    )
    assert res_bad_key.status_code == 401

    # 3. Valid API key
    res_valid = client.post(
        "/internal/simplify",
        headers=VALID_HEADERS,
        json=payload,
    )
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["mode"] == "detailed"
    assert "explanation" in data
    assert len(data["glossary"]) > 0
    assert len(data["what_could_be_missed"]) > 0
    assert data["is_grounded"] is True


def test_simplify_endpoint_with_auth():
    payload = {
        "text": "The provisions of Section 8 are severable.",
        "mode": "professional",
    }
    res = client.post("/simplify", headers=VALID_HEADERS, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "professional"
    assert data["is_grounded"] is True
