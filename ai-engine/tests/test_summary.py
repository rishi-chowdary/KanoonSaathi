import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pydantic import BaseModel
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
from app.providers.base import LLMProvider
from app.providers.mock_provider import MockProvider
from app.providers.gemini_provider import GeminiProvider
from app.services.llm_validator import generate_with_retry
from google.genai.errors import APIError

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


class FlakyProvider(LLMProvider):
    def __init__(self, failure_count: int, valid_response: DocumentSummaryResponse):
        self.calls = 0
        self.failure_count = failure_count
        self.valid_response = valid_response
        self.prompts_received = []

    @property
    def provider_name(self) -> str:
        return "flaky"

    @property
    def model_name(self) -> str:
        return "flaky-v1"

    async def generate_structured(self, prompt, schema, system_prompt=None, temperature=0.1):
        self.calls += 1
        self.prompts_received.append(prompt)
        if self.calls <= self.failure_count:
            raise ValueError(f"Simulated schema validation error: missing required fields on attempt {self.calls}")
        return self.valid_response


@pytest.mark.anyio
async def test_json_validation_retry_path_two_failures_then_valid():
    valid_summary = DocumentSummaryResponse(
        title="Valid Agreement",
        document_type="NDA",
        purpose="Protection",
        parties=[PartyItem(name="Acme", role="Discloser", evidence_quote="Acme", source_page=1)],
        main_conditions=[],
        obligations=[],
        financial_terms=[],
        short_summary="Short",
        detailed_summary="Detailed",
    )
    # Fail twice, succeed on attempt 3 (max_retries=2 allows 3 total attempts: attempt 0, 1, 2)
    flaky = FlakyProvider(failure_count=2, valid_response=valid_summary)

    result = await generate_with_retry(
        provider=flaky,
        prompt="Initial prompt",
        schema=DocumentSummaryResponse,
        max_retries=2,
    )

    assert flaky.calls == 3
    assert result.title == "Valid Agreement"
    assert "PREVIOUS ATTEMPT FAILED SCHEMA VALIDATION" in flaky.prompts_received[1]
    assert "PREVIOUS ATTEMPT FAILED SCHEMA VALIDATION" in flaky.prompts_received[2]


@pytest.mark.anyio
async def test_json_validation_retry_path_exceeds_max_retries():
    valid_summary = DocumentSummaryResponse(
        title="Valid Agreement",
        document_type="NDA",
        purpose="Protection",
        short_summary="Short",
        detailed_summary="Detailed",
    )
    # Fail 3 times when max_retries=2 -> must raise ValueError
    flaky = FlakyProvider(failure_count=3, valid_response=valid_summary)

    with pytest.raises(ValueError):
        await generate_with_retry(
            provider=flaky,
            prompt="Initial prompt",
            schema=DocumentSummaryResponse,
            max_retries=2,
        )
    assert flaky.calls == 3


@pytest.mark.anyio
async def test_gemini_provider_backoff_on_simulated_429():
    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        provider = GeminiProvider(api_key="test-key", model_name="gemini-1.5-flash")

        # Simulate 429 error twice, then successful response
        err_429 = APIError(code=429, response_json={"error": {"code": 429, "message": "Resource exhausted"}})

        valid_mock_response = MagicMock()
        valid_mock_response.text = '{"title": "Test Title", "document_type": "NDA", "purpose": "Confidentiality", "parties": [], "main_conditions": [], "obligations": [], "financial_terms": [], "short_summary": "Short", "detailed_summary": "Detailed"}'
        valid_mock_response.usage_metadata.prompt_token_count = 100
        valid_mock_response.usage_metadata.candidates_token_count = 50

        mock_client.models.generate_content.side_effect = [err_429, err_429, valid_mock_response]

        # Intercept asyncio.sleep so tests execute instantly without real delay
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            res = await provider.generate_structured(
                prompt="test prompt",
                schema=DocumentSummaryResponse,
            )

            assert res.title == "Test Title"
            assert mock_client.models.generate_content.call_count == 3
            assert mock_sleep.call_count == 2


