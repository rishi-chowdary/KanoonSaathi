import os
import pytest
from fastapi.testclient import TestClient

os.environ["USE_MOCK_LLM"] = "true"

from app.main import app
from app.config import settings
from app.providers.mock_provider import MockProvider
from app.schemas.risk import RiskAnalysisRequest, RiskAnalysisResponse
from app.services.risk_service import analyze_risks, filter_rule7_language

client = TestClient(app)
VALID_HEADERS = {"X-Internal-Api-Key": settings.internal_api_key}


def test_rule7_language_filter():
    forbidden_text = (
        "This clause is illegal and null and void under state statutes. It is unenforceable and violates the law."
    )
    filtered = filter_rule7_language(forbidden_text)
    assert "illegal" not in filtered.lower()
    assert "void" not in filtered.lower()
    assert "unenforceable" not in filtered.lower()
    assert "violates the law" not in filtered.lower()
    assert "may face legal enforceability issues" in filtered or "validity" in filtered


@pytest.mark.anyio
async def test_analyze_risks_mock_provider():
    provider = MockProvider()
    request = RiskAnalysisRequest(
        document_id="test-doc-123",
        pages=[
            {
                "page_number": 1,
                "text": "Contractor shall indemnify and hold harmless Company from any and all damages. Non-breaching party may terminate immediately if breach is not cured within 5 days.",
            }
        ],
        governing_law_found=False,
    )

    response = await analyze_risks(request, provider)
    assert isinstance(response, RiskAnalysisResponse)
    assert response.total_risks == 2
    assert response.high_risks == 1
    assert response.medium_risks == 1
    assert response.governing_law_found is False
    assert response.jurisdiction_warning is not None
    assert response.risks[0].jurisdiction_caveat is not None
    assert response.risks[0].quote_verified is True
    assert response.risks[0].source_page == 1


def test_risks_endpoint_auth():
    payload = {
        "document_id": "test-doc-123",
        "pages": [{"page_number": 1, "text": "Some contract text"}],
    }

    # 1. Missing key
    res_no_key = client.post("/internal/analyze/risks", json=payload)
    assert res_no_key.status_code == 401

    # 2. Valid key
    res_valid = client.post("/internal/analyze/risks", headers=VALID_HEADERS, json=payload)
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert "risks" in data
    assert len(data["risks"]) > 0

