import os
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

# Ensure mock LLM is used for tests
os.environ["USE_MOCK_LLM"] = "true"

from app.main import app
from app.config import settings
from app.providers.mock_provider import MockProvider
from app.schemas.clause import (
    BatchExplanationsResponse,
    ChunkClauseExtraction,
    ClauseAnalysisRequest,
    ClauseAnalysisResponse,
    ClauseExplanations,
    ClauseItem,
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

    # Same section reference and category -> duplicate
    assert is_duplicate_clause(clause1, clause2) is True

    # Merge keeps longer original text, higher importance, earlier page
    merged = merge_clauses(clause1, clause2)
    assert "written notice to the other party" in merged.original_text
    assert merged.importance == "HIGH"
    assert merged.source_page == 2
    assert merged.section_reference == "Section 5.1"


def test_dedupe_overlap_and_distinct_clauses():
    # Text overlap / substring match
    full_clause = RawClauseItem(
        title="Confidential Information Protection",
        category="Confidentiality",
        original_text="The receiving party agrees to safeguard and protect all confidential information and trade secrets.",
        evidence_quote="safeguard and protect all confidential information",
        importance="HIGH",
        affected_party="Receiving Party",
        source_page=1,
    )
    partial_clause = RawClauseItem(
        title="Confidentiality Obligations",
        category="Confidentiality",
        original_text="The receiving party agrees to safeguard and protect all confidential information",
        evidence_quote="safeguard and protect all confidential information",
        importance="MEDIUM",
        affected_party="Receiving Party",
        source_page=1,
    )
    assert is_duplicate_clause(full_clause, partial_clause) is True

    # Distinct clauses must NOT be deduplicated
    distinct_clause = RawClauseItem(
        title="Governing Law",
        category="Governing Law",
        original_text="This agreement is governed by the laws of the State of New York.",
        evidence_quote="laws of the State of New York",
        importance="LOW",
        affected_party="Both parties",
        source_page=4,
        section_reference="Section 12",
    )
    assert is_duplicate_clause(full_clause, distinct_clause) is False


def test_validate_numbers_and_dates_consistency():
    original_text = (
        "The Recipient shall pay a fee of $5,000 within thirty (30) days of invoice date, ending in October. Royalty rate is 15%."
    )

    # Valid explanations matching original figures
    valid_explanations = {
        "simple": "You must pay $5,000 within 30 days of the invoice, before October. The rate is 15%.",
        "detailed": "Requires full settlement of the $5,000 payment obligation within thirty (30) days, ending in October, at a 15% rate.",
        "professional": "Imposes a $5,000 payment deadline within 30 days of billing at a 15% rate.",
    }
    is_ok, warnings = validate_numbers_and_dates(original_text, valid_explanations)
    assert is_ok is True
    assert len(warnings) == 0

    # Hallucinated dollar amount ($15,000 instead of $5,000)
    hallucinated_dollar = {"simple": "Payment of $15,000 is required."}
    is_ok, warnings = validate_numbers_and_dates(original_text, hallucinated_dollar)
    assert is_ok is False
    assert any("15,000" in w for w in warnings)

    # Hallucinated timeframe (60 days instead of 30 days)
    hallucinated_days = {"detailed": "Must be paid within 60 days."}
    is_ok, warnings = validate_numbers_and_dates(original_text, hallucinated_days)
    assert is_ok is False
    assert any("60" in w for w in warnings)

    # Hallucinated percentage (25% instead of 15%)
    hallucinated_pct = {"detailed": "Royalty is set at 25%."}
    is_ok, warnings = validate_numbers_and_dates(original_text, hallucinated_pct)
    assert is_ok is False
    assert any("25%" in w or "25" in w for w in warnings)

    # Hallucinated calendar month (December instead of October)
    hallucinated_month = {"professional": "Agreement lapses in December."}
    is_ok, warnings = validate_numbers_and_dates(original_text, hallucinated_month)
    assert is_ok is False
    assert any("December" in w for w in warnings)

    # Single digits in numbering/steps are permitted without false-positive alarms
    formatting_digits = {
        "simple": "Step 1: Review invoice. Step 2: Pay $5,000 within 30 days."
    }
    is_ok, warnings = validate_numbers_and_dates(original_text, formatting_digits)
    assert is_ok is True


def test_clause_schema_validation():
    # Valid RawClauseItem
    valid_raw = RawClauseItem(
        title="Mutual Non-Disclosure",
        category="Confidentiality",
        original_text="Both parties agree not to disclose confidential information.",
        evidence_quote="not to disclose confidential information",
        importance="HIGH",
        affected_party="Both parties",
        source_page=1,
    )
    assert valid_raw.importance == "HIGH"
    assert valid_raw.category == "Confidentiality"

    # Invalid importance value raises ValidationError
    with pytest.raises(ValidationError):
        RawClauseItem(
            title="Invalid Clause",
            category="Termination",
            original_text="Text",
            evidence_quote="Text",
            importance="SUPER_HIGH",  # Not in Literal["HIGH", "MEDIUM", "LOW"]
        )

    # Missing required original_text raises ValidationError
    with pytest.raises(ValidationError):
        RawClauseItem(
            title="Missing Text Clause",
            category="Termination",
            evidence_quote="Quote",
        )

    # Valid BatchExplanationsResponse
    batch_resp = BatchExplanationsResponse(
        explanations=[
            ClauseExplanations(
                clause_index=0,
                simplified_simple="Simple version",
                simplified_detailed="Detailed version preserving exceptions",
                simplified_professional="Executive business version",
            )
        ]
    )
    assert len(batch_resp.explanations) == 1
    assert batch_resp.explanations[0].clause_index == 0

    # Valid ClauseAnalysisResponse
    full_resp = ClauseAnalysisResponse(
        document_id="doc-999",
        clauses=[
            ClauseItem(
                title="Governing Law",
                category="Governing Law",
                original_text="Delaware law applies.",
                simplified_simple="Delaware law applies to this deal.",
                simplified_detailed="Any dispute arising out of this agreement will be decided under Delaware law.",
                simplified_professional="Designates State of Delaware as governing legal jurisdiction.",
                importance="LOW",
                affected_party="Both parties",
                source_page=1,
                evidence_quote="Delaware law applies",
                quote_verified=True,
                provenance="EXTRACTED",
                numbers_dates_verified=True,
            )
        ],
        total_clauses=1,
        verification_rate=100.0,
    )
    assert full_resp.verification_rate == 100.0
    assert full_resp.clauses[0].quote_verified is True


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
