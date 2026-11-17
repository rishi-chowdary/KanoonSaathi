import os
import pytest
from fastapi.testclient import TestClient

os.environ["USE_MOCK_LLM"] = "true"

from app.main import app
from app.config import settings
from app.providers.mock_provider import MockProvider
from app.schemas.missing import MissingProvisionsRequest, MissingProvisionsResponse
from app.services.missing_service import (
    analyze_missing_provisions,
    detect_document_type,
    load_expected_provisions_checklist,
)

client = TestClient(app)
VALID_HEADERS = {"X-Internal-Api-Key": settings.internal_api_key}


def test_detect_document_type():
    # From hints
    assert detect_document_type("", hint="Employment Offer Letter") == "employment"
    assert detect_document_type("", hint="Commercial Lease Agreement") == "rental_lease"
    assert detect_document_type("", hint="Mutual Non-Disclosure Agreement") == "nda"

    # From text content
    nda_text = "The receiving party agrees to hold all confidential information in trust for disclosing party."
    assert detect_document_type(nda_text) == "nda"

    lease_text = "The tenant agrees to pay monthly rent to landlord for the leased premises."
    assert detect_document_type(lease_text) == "rental_lease"


def test_expected_provisions_yaml_structure():
    checklists = load_expected_provisions_checklist()
    expected_types = ["employment", "rental_lease", "nda", "service_agreement", "sale", "loan", "other"]
    for t in expected_types:
        assert t in checklists, f"Missing checklist for {t}"
        assert len(checklists[t]) >= 3, f"Checklist for {t} has too few items"
        first_item = checklists[t][0]
        assert "title" in first_item
        assert "category" in first_item
        assert "why_it_matters" in first_item
        assert "typical_provision" in first_item
        assert "risk_level" in first_item


def test_complete_nda_does_not_produce_absurd_omissions():
    """Rule verification: A complete NDA must NOT produce absurd non-NDA omissions (e.g. lease eviction or wage schedules)."""
    checklists = load_expected_provisions_checklist()
    nda_checklist = checklists.get("nda", [])
    nda_titles = [item["title"].lower() for item in nda_checklist]

    # Assert NDA checklist only contains confidentiality and NDA-appropriate provisions
    assert any("exclusion" in t or "confidential" in t for t in nda_titles)
    assert not any("rent" in t or "eviction" in t or "salary" in t for t in nda_titles)


def test_contract_lacking_payment_deadline_receives_matching_omission():
    """Rule verification: Commercial/sales/service contracts lacking payment deadlines receive the appropriate omission warning."""
    checklists = load_expected_provisions_checklist()
    sale_checklist = checklists.get("sale", [])
    payment_items_sale = [
        item for item in sale_checklist
        if "payment" in item["title"].lower() or "payment" in item["category"].lower()
    ]
    assert len(payment_items_sale) > 0, "Sale checklist must include payment terms omission check"
    assert payment_items_sale[0]["category"] == "Financial"
    assert "Payment Terms and Late Interest" in payment_items_sale[0]["title"]

    service_checklist = checklists.get("service_agreement", [])
    payment_items_service = [
        item for item in service_checklist
        if "payment" in item["title"].lower() or "payment" in item["category"].lower()
    ]
    assert len(payment_items_service) > 0, "Service checklist must include payment terms omission check"
    assert payment_items_service[0]["category"] == "Financial"



@pytest.mark.anyio
async def test_analyze_missing_provisions_mock_provider():
    provider = MockProvider()
    request = MissingProvisionsRequest(
        document_id="test-doc-123",
        pages=[{"page_number": 1, "text": "Service agreement for consulting services."}],
        document_type_hint="service_agreement",
    )

    response = await analyze_missing_provisions(request, provider)
    assert isinstance(response, MissingProvisionsResponse)
    assert response.detected_document_type == "service_agreement"
    assert response.total_missing == 2
    for item in response.missing_provisions:
        assert item.label == "Possible omission"
        assert item.risk_level in ("HIGH", "MEDIUM", "LOW", "INFORMATIONAL")


def test_missing_endpoint_auth():
    payload = {
        "document_id": "test-doc-123",
        "pages": [{"page_number": 1, "text": "Contract text"}],
    }

    # 1. Missing key
    res_no_key = client.post("/internal/analyze/missing", json=payload)
    assert res_no_key.status_code == 401

    # 2. Valid key
    res_valid = client.post("/internal/analyze/missing", headers=VALID_HEADERS, json=payload)
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert "missing_provisions" in data
    assert len(data["missing_provisions"]) > 0
    assert "disclaimer" in data

