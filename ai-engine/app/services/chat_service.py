import logging
from pathlib import Path
from app.providers.base import LLMProvider
from app.schemas.extraction import PageExtraction
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    RawChatResult,
    StructuredCitation,
)
from app.services.quote_verifier import verify_quote
from app.services.risk_service import filter_rule7_language

logger = logging.getLogger("ai_engine.chat_service")

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "v1" / "chat_prompt.txt"


def format_chunks_for_prompt(chunks) -> str:
    if not chunks:
        return "(No document chunks retrieved)"
    parts = []
    for i, c in enumerate(chunks):
        page_num = getattr(c, "page_number", 1)
        content = getattr(c, "content", "")
        parts.append(f'<chunk index="{i + 1}" page="{page_num}">\n{content}\n</chunk>')
    return "\n\n".join(parts)


def format_history_for_prompt(history) -> str:
    if not history:
        return "(No prior conversation history)"
    lines = []
    for m in history:
        role_label = "User" if m.role == "user" else "Assistant"
        lines.append(f"{role_label}: {m.content}")
    return "\n".join(lines)


async def answer_chat_question(
    request: ChatRequest,
    provider: LLMProvider,
) -> ChatResponse:
    """Answers user contract questions strictly grounded in retrieved chunks with quote verification."""
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    chunks_text = format_chunks_for_prompt(request.retrieved_chunks)
    history_text = format_history_for_prompt(request.conversation_history)

    prompt = prompt_template.format(
        chunks_text=chunks_text,
        history_text=history_text,
        question=request.question,
    )

    logger.info(
        "executing grounded chat via %s for question '%s' across %d chunks",
        provider.provider_name,
        request.question[:40],
        len(request.retrieved_chunks),
    )

    raw_result: RawChatResult = await provider.generate_structured(
        prompt=prompt,
        schema=RawChatResult,
        system_prompt=(
            "You are a professional legal AI assistant that answers questions strictly "
            "using the provided document excerpts. Answer concisely and cite source pages with verbatim quotes."
        ),
        temperature=0.1,
    )

    # Sanitize answer against Rule 7
    sanitized_answer = filter_rule7_language(raw_result.answer)

    # Create PageExtraction wrappers for quote verification
    pseudo_pages = [
        PageExtraction(page_number=c.page_number, text=c.content)
        for c in request.retrieved_chunks
    ]

    verified_citations: list[StructuredCitation] = []
    for cit in raw_result.citations:
        if not cit.quote or not cit.quote.strip():
            continue

        is_verified, actual_page = verify_quote(
            quote=cit.quote,
            pages=pseudo_pages,
            claimed_page=cit.page,
        )

        verified_citations.append(
            StructuredCitation(
                page=actual_page if is_verified else cit.page,
                section_ref=cit.section_ref,
                quote=cit.quote,
                quote_verified=is_verified,
            )
        )

    addressed = raw_result.confidence != "not found"

    return ChatResponse(
        answer=sanitized_answer,
        citations=verified_citations,
        confidence=raw_result.confidence,
        addressed_in_document=addressed,
    )
