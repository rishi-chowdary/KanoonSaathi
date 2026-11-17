import os
import pytest
from fastapi.testclient import TestClient

os.environ["USE_MOCK_LLM"] = "true"

from app.main import app
from app.config import settings
from app.providers.mock_provider import MockProvider
from app.schemas.key_info import FactItem, KeyInfoRequest, KeyInfoResponse
from app.services.key_info_service import extract_key_info, normalize_fact_item

client = TestClient(app)
VALID_HEADERS = {"X-Internal-Api-Key": settings.internal_api_key}


def test_normalize_fact_item_rule6():
    # Empty / none string -> exactly "Not specified"
    f1 = FactItem(value="")
    norm1 = normalize_fact_item(f1, [])
    assert norm1.value == "Not specified"
    assert norm1.source_page is None
    assert norm1.evidence_quote is None
    assert norm1.quote_verified is False

    f2 = FactItem(value="N/A", evidence_quote="none")
    norm2 = normalize_fact_item(f2, [])
    assert norm2.value == "Not specified"
    assert norm2.evidence_quote is None


@pytest.mark.anyio
async def test_extract_key_info_mock_provider():
    provider = MockProvider()
    request = KeyInfoRequest(
        document_id="test-doc-123",
        pages=[
            {
                "page_number": 1,
                "text": "Total fee of $50,000.00 payable Net 30 days from invoice, accruing 1.5% monthly late interest, commencing on October 1, 2026.",
            },
            {
                "page_number": 2,
                "text": "Terminating on September 30, 2027 upon 30 days written notice, or material breach following 30-day cure.",
            },
        ],
    )

    response = await extract_key_info(request, provider)
    assert isinstance(response, KeyInfoResponse)
    assert response.contract_amount.value == "$50,000.00"
    assert response.contract_amount.quote_verified is True
    assert response.renewal_date.value == "Not specified"
    assert response.renewal_date.source_page is None
    assert len(response.obligations) == 2
    assert len(response.important_dates) == 2


def test_key_info_endpoint_auth():
    payload = {
        "document_id": "test-doc-123",
        "pages": [{"page_number": 1, "text": "Contract terms"}],
    }

    # 1. Missing key
    res_no_key = client.post("/internal/analyze/key-info", json=payload)
    assert res_no_key.status_code == 401

    # 2. Valid key
    res_valid = client.post("/internal/analyze/key-info", headers=VALID_HEADERS, json=payload)
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["contract_amount"]["value"] == "$50,000.00"
    assert data["renewal_date"]["value"] == "Not specified"

