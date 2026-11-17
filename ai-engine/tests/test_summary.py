import os
import pytest
from fastapi.testclient import TestClient

# Ensure mock LLM is used for tests
os.environ["USE_MOCK_LLM"] = "true"

from app.main import app
from app.config import settings
from app.schemas.extraction import PageExtraction, ChunkExtraction
from app.schemas.summary import (
    DocumentSummaryRequest,
    DocumentSummaryResponse,
    PartyItem,
    GroundedItem,
)
from app.services.quote_verifier import verify_quote, verify_summary_quotes
from app.providers.mock_provider import MockProvider

client = TestClient(app)
VALID_HEADERS = {"X-Internal-Api-Key": settings.internal_api_key}


def test_quote_verifier_exact_match():
    pages = [
        PageExtraction(
            page_number=1,
            text="The Recipient agrees to hold the Confidential Information in strict confidence.",
            ocr_used=False,
        ),
        PageExtraction(
            page_number=2,
            text="This agreement is governed by the laws of the State of Delaware.",
            ocr_used=False,
        ),
    ]

    is_verified, page_num = verify_quote(
        "hold the Confidential Information in strict confidence",
        pages,
        claimed_page=1,
    )
    assert is_verified is True
    assert page_num == 1


def test_quote_verifier_fuzzy_match():
    pages = [
        PageExtraction(
            page_number=1,
            text="The Recipient agrees to   hold the Confidential Information in strict confidence.",
            ocr_used=False,
        )
    ]

    # Minor variation with extra spaces and case
    is_verified, page_num = verify_quote(
        "HOLD THE CONFIDENTIAL INFORMATION IN STRICT CONFIDENCE",
        pages,
        claimed_page=1,
    )
    assert is_verified is True
    assert page_num == 1


def test_quote_verifier_rejects_hallucination():
    pages = [
        PageExtraction(
            page_number=1,
            text="The Recipient agrees to hold the Confidential Information in strict confidence.",
            ocr_used=False,
        )
    ]

    is_verified, _ = verify_quote(
        "Party shall pay a fine of five million dollars upon early termination",
        pages,
        claimed_page=1,
    )
    assert is_verified is False


def test_verify_summary_quotes_calculates_rate():
    pages = [
        PageExtraction(
            page_number=1,
            text="Acme Corporation (\"Disclosing Party\") and Beta LLC (\"Receiving Party\").",
            ocr_used=False,
        )
    ]

    summary = DocumentSummaryResponse(
        title="Sample NDA",
        document_type="NDA",
        purpose="Confidentiality",
        parties=[
            PartyItem(name="Acme Corporation", role="Discloser", evidence_quote="Acme Corporation", source_page=1),
            PartyItem(name="Beta LLC", role="Recipient", evidence_quote="Beta LLC", source_page=1),
        ],
        main_conditions=[
            GroundedItem(text="Keep secret", evidence_quote="Non-existent fake quote", source_page=1),
        ],
        obligations=[],
        financial_terms=[],
        short_summary="Summary",
        detailed_summary="Detailed summary",
        llm_provider="mock",
        llm_model="mock-v1",
    )

    verified = verify_summary_quotes(summary, pages)
    assert verified.parties[0].quote_verified is True
    assert verified.parties[1].quote_verified is True
    assert verified.main_conditions[0].quote_verified is False
    # 2 out of 3 verified = 66.67%
    assert 60.0 <= verified.verification_rate <= 70.0


@pytest.mark.anyio
async def test_mock_provider_structured():
    provider = MockProvider()
    res = await provider.generate_structured(
        prompt="<document_content>Acme Corporation discloses confidential data to Beta LLC.</document_content>",
        schema=DocumentSummaryResponse,
    )
    assert res.title != ""
    assert len(res.parties) >= 2
    assert res.short_summary != ""


def test_analyze_summary_endpoint():
    req = DocumentSummaryRequest(
        document_id="123e4567-e89b-12d3-a456-426614174000",
        pages=[
            PageExtraction(
                page_number=1,
                text="NON-DISCLOSURE AGREEMENT\nBetween Acme Corporation and Beta Technologies LLC.",
                ocr_used=False,
            )
        ],
        chunks=[
            ChunkExtraction(
                chunk_index=0,
                page_start=1,
                page_end=1,
                content="NON-DISCLOSURE AGREEMENT\nBetween Acme Corporation and Beta Technologies LLC.",
                token_count=10,
            )
        ],
    )

    response = client.post(
        "/internal/analyze/summary",
        headers=VALID_HEADERS,
        json=req.model_dump(),
    )
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "document_type" in data
    assert "purpose" in data
    assert "parties" in data
    assert len(data["parties"]) >= 1
    assert "short_summary" in data
    assert "detailed_summary" in data
    assert "verification_rate" in data
    assert data["llm_provider"] in ["mock", "gemini", "ollama"]


def test_analyze_summary_requires_auth():
    response = client.post(
        "/internal/analyze/summary",
        json={"document_id": "test", "pages": [], "chunks": []},
    )
    assert response.status_code == 401
