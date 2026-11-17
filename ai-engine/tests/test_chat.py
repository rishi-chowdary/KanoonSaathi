import os
import pytest
from fastapi.testclient import TestClient

os.environ["USE_MOCK_LLM"] = "true"

from app.main import app
from app.config import settings
from app.providers.mock_provider import MockProvider
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    RetrievedChunkItem,
    ChatMessageItem,
)
from app.services.chat_service import answer_chat_question

client = TestClient(app)
VALID_HEADERS = {"X-Internal-Api-Key": settings.internal_api_key}


@pytest.mark.anyio
async def test_chat_service_supported_answer_with_citations():
    provider = MockProvider()
    request = ChatRequest(
        question="What is the notice period for terminating without cause?",
        retrieved_chunks=[
            RetrievedChunkItem(
                chunk_id="chunk-1",
                page_number=2,
                content="Company may terminate Employee employment at any time without cause upon thirty (30) days prior written notice.",
                section_ref="Section 6",
            )
        ],
        conversation_history=[
            ChatMessageItem(role="user", content="Hello, who is the employee?"),
            ChatMessageItem(role="assistant", content="The employee is David Chen."),
        ],
    )

    response = await answer_chat_question(request, provider)
    assert isinstance(response, ChatResponse)
    assert "thirty (30) days" in response.answer
    assert response.confidence == "supported"
    assert response.addressed_in_document is True
    assert len(response.citations) > 0
    assert response.citations[0].page == 2
    assert response.citations[0].quote_verified is True
    assert "thirty (30) days" in response.citations[0].quote


@pytest.mark.anyio
async def test_chat_service_unaddressed_question():
    provider = MockProvider()
    request = ChatRequest(
        question="What is the weather policy for dogs?",
        retrieved_chunks=[
            RetrievedChunkItem(
                chunk_id="chunk-1",
                page_number=1,
                content="Executive Employment Agreement between Apex and Employee.",
            )
        ],
    )

    response = await answer_chat_question(request, provider)
    assert isinstance(response, ChatResponse)
    assert response.confidence == "not found"
    assert response.addressed_in_document is False
    assert "does not appear to address" in response.answer


def test_chat_endpoint_requires_auth():
    payload = {
        "question": "What is the notice period?",
        "retrieved_chunks": [
            {
                "page_number": 1,
                "content": "Notice period is 30 days.",
            }
        ],
    }

    # Missing API Key
    res_no_key = client.post("/internal/chat", json=payload)
    assert res_no_key.status_code == 401

    # Valid API Key
    res_valid = client.post("/internal/chat", headers=VALID_HEADERS, json=payload)
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert "answer" in data
    assert "citations" in data
    assert "confidence" in data
    assert "addressed_in_document" in data
