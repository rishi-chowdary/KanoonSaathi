import os
import pytest
from fastapi.testclient import TestClient

# Ensure mock LLM is used for tests
os.environ["USE_MOCK_LLM"] = "true"

from app.main import app
from app.config import settings
from app.providers.mock_provider import MockProvider
from app.schemas.clause import (
    ClauseAnalysisRequest,
    ClauseAnalysisResponse,
    RawClauseItem,
)
from app.schemas.extraction import ChunkExtraction, PageExtraction
from app.services.clause_service import (
    analyze_document_clauses,
    is_duplicate_clause,
    merge_clauses,
    validate_numbers_and_dates,
)

client = TestClient(app)
VALID_HEADERS = {"X-Internal-Api-Key": settings.internal_api_key}


def test_is_duplicate_clause_and_merge():
    clause1 = RawClauseItem(
        title="Termination",
        category="Termination",
        custom_label=None,
        original_text="Either party may terminate this agreement with 30 days notice.",
        evidence_quote="with 30 days notice",
        importance="MEDIUM",
        affected_party="Both parties",
        source_page=2,
        section_reference="Section 5.1",
    )

    clause2 = RawClauseItem(
        title="Termination Clause",
        category="Termination",
        custom_label=None,
        original_text="Either party may terminate this agreement with 30 days written notice to the other party.",
        evidence_quote="with 30 days written notice",
        importance="HIGH",
        affected_party="Both parties",
        source_page=3,
        section_reference="Section 5.1",
    )

    # Same section reference and category
    assert is_duplicate_clause(clause1, clause2) is True

    # Merge keeps longer original text, higher importance, earlier page
    merged = merge_clauses(clause1, clause2)
    assert "written notice to the other party" in merged.original_text
    assert merged.importance == "HIGH"
    assert merged.source_page == 2
    assert merged.section_reference == "Section 5.1"


def test_validate_numbers_and_dates():
    original_text = (
        "The Recipient shall pay a fee of $5,000 within thirty (30) days of invoice date, ending in October."
    )

    # Valid explanations with matching numbers and months
    valid_explanations = {
        "simple": "You have to pay $5,000 within 30 days of the invoice, before October.",
        "detailed": "Requires full settlement of the $5,000 payment obligation within thirty (30) days.",
        "professional": "Imposes a $5,000 payment deadline within 30 days of billing.",
    }
    is_ok, warnings = validate_numbers_and_dates(original_text, valid_explanations)
    assert is_ok is True
    assert len(warnings) == 0

    # Hallucinated number (e.g. 90 days or $15,000)
    hallucinated_num = {
        "simple": "You must pay $15,000 within 90 days.",
    }
    is_ok2, warnings2 = validate_numbers_and_dates(original_text, hallucinated_num)
    assert is_ok2 is False
    assert any("15,000" in w or "90" in w for w in warnings2)

    # Hallucinated month (e.g. December)
    hallucinated_date = {
        "detailed": "Payment must be completed by December.",
    }
    is_ok3, warnings3 = validate_numbers_and_dates(original_text, hallucinated_date)
    assert is_ok3 is False
    assert any("December" in w for w in warnings3)


@pytest.mark.anyio
async def test_analyze_document_clauses_mock():
    mock_provider = MockProvider()

    pages = [
        PageExtraction(
            page_number=1,
            text=(
                "CONFIDENTIALITY AGREEMENT\n"
                "Recipient agrees to hold all Confidential Information in strict confidence and not disclose it to any third party for a period of thirty (30) days.\n"
                "Either party may terminate this Agreement by providing thirty (30) days prior written notice.\n"
                "The contractor must adhere to the designated data isolation guidelines."
            ),
            ocr_used=False,
        )
    ]

    chunks = [
        ChunkExtraction(
            chunk_index=0,
            page_start=1,
            page_end=1,
            content=pages[0].text,
            token_count=100,
        )
    ]

    response = await analyze_document_clauses(
        document_id="test-doc-123",
        pages=pages,
        chunks=chunks,
        provider=mock_provider,
    )

    assert response.document_id == "test-doc-123"
    assert response.total_clauses == 3
    assert len(response.clauses) == 3

    # Check first clause
    conf_clause = response.clauses[0]
    assert conf_clause.category == "Confidentiality"
    assert conf_clause.importance == "HIGH"
    assert conf_clause.quote_verified is True
    assert "30 days" in conf_clause.simplified_simple
    assert conf_clause.numbers_dates_verified is True

    # Check "Other" category handling
    other_clause = response.clauses[2]
    assert other_clause.category == "Other"
    assert other_clause.custom_label == "Security Standards"
    assert other_clause.quote_verified is True

    # Verification rate should be 100% since all mock quotes are in page text
    assert response.verification_rate == 100.0


def test_analyze_clauses_endpoint():
    req = ClauseAnalysisRequest(
        document_id="test-endpoint-doc",
        pages=[
            PageExtraction(
                page_number=1,
                text="Recipient agrees to hold all Confidential Information in strict confidence and not disclose it to any third party for a period of thirty (30) days.",
                ocr_used=False,
            )
        ],
        chunks=[
            ChunkExtraction(
                chunk_index=0,
                page_start=1,
                page_end=1,
                content="Recipient agrees to hold all Confidential Information in strict confidence and not disclose it to any third party for a period of thirty (30) days.",
                token_count=30,
            )
        ],
    )

    # Protected endpoint requires internal API key
    unauth_resp = client.post("/internal/analyze/clauses", json=req.model_dump())
    assert unauth_resp.status_code in (401, 403)

    # Valid internal call
    resp = client.post("/internal/analyze/clauses", headers=VALID_HEADERS, json=req.model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert data["document_id"] == "test-endpoint-doc"
    assert len(data["clauses"]) >= 1
    assert "simplified_simple" in data["clauses"][0]
    assert "simplified_detailed" in data["clauses"][0]
    assert "simplified_professional" in data["clauses"][0]
