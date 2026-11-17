import json
from pathlib import Path
import pytest
from app.services.quote_verifier import verify_quote
from app.schemas.extraction import PageExtraction
from app.services.missing_service import detect_document_type, load_expected_provisions_checklist
from app.schemas.chat import RetrievedChunkItem, StructuredCitation


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_contract_fixture.json"


@pytest.fixture
def recorded_contract():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_recorded_fixture_structure(recorded_contract):
    assert "document_id" in recorded_contract
    assert len(recorded_contract["pages"]) == 2
    assert len(recorded_contract["chunks"]) == 2
    assert len(recorded_contract["expected_clauses"]) >= 3


def test_recorded_clauses_quote_verification(recorded_contract):
    pages = [
        PageExtraction(
            page_number=p["page_number"],
            text=p["text"],
            tables=[],
            ocr_used=False
        )
        for p in recorded_contract["pages"]
    ]
    clauses = recorded_contract["expected_clauses"]

    verified_count = 0
    for clause in clauses:
        quote = clause["evidence_quote"]
        claimed_page = clause["source_page"]
        verified, matched_page = verify_quote(quote, pages, claimed_page=claimed_page)
        assert verified, f"Quote '{quote}' failed verification against pages"
        assert matched_page == claimed_page
        verified_count += 1

    verification_rate = verified_count / len(clauses)
    assert verification_rate == 1.0, f"Expected 100% verification, got {verification_rate}"


def test_recorded_risks_forbidden_phrases(recorded_contract):
    forbidden = ["illegal", "void", "unenforceable"]
    risks = recorded_contract.get("expected_risks", [])

    for risk in risks:
        for field in ["title", "explanation", "why_it_matters"]:
            val = risk.get(field, "").lower()
            for word in forbidden:
                assert word not in val, f"Forbidden word '{word}' found in risk {field}"


def test_recorded_missing_provisions_checklist(recorded_contract):
    doc_type = recorded_contract["document_type"]
    category = detect_document_type("", hint=doc_type)
    all_checklists = load_expected_provisions_checklist()
    checklist = all_checklists.get(category, [])

    assert len(checklist) >= 3
    names = [item["title"] for item in checklist]
    assert any("Termination" in name or "Dispute" in name or "Liability" in name or "Payment" in name or "Compensation" in name for name in names)


def test_recorded_chat_grounded_citation(recorded_contract):
    chunks = [
        RetrievedChunkItem(
            chunk_id=f"c-{c['chunk_index']}",
            page_number=c["page_start"],
            content=c["content"],
            section_ref=None
        )
        for c in recorded_contract["chunks"]
    ]

    quote = "Invoices are payable net 30 days from the invoice date."
    matching_chunk = next((c for c in chunks if "payable net 30 days" in c.content), None)
    assert matching_chunk is not None
    assert matching_chunk.page_number == 2

    citation = StructuredCitation(
        page=matching_chunk.page_number,
        section_ref="3. Fees and Payment Terms",
        quote=quote,
        quote_verified=True
    )
    assert citation.page == 2
    assert citation.quote_verified is True
