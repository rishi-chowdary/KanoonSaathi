import logging
from app.prompts import load_prompt
from app.providers.base import LLMProvider
from app.schemas.extraction import PageExtraction, ChunkExtraction
from app.schemas.summary import (
    DocumentSummaryResponse,
    ChunkSummaryExtraction,
)
from app.services.llm_validator import generate_with_retry
from app.services.quote_verifier import verify_summary_quotes

logger = logging.getLogger("ai_engine.summary_service")


async def analyze_document_summary(
    document_id: str,
    pages: list[PageExtraction],
    chunks: list[ChunkExtraction],
    provider: LLMProvider,
) -> DocumentSummaryResponse:
    """Execute map-reduce summarization pipeline over document chunks, followed by evidence quote verification."""
    system_prompt = load_prompt("system_prompt", "v1")

    # If no chunks provided, synthesize one from pages
    if not chunks and pages:
        full_text = "\n\n".join(f"[Page {p.page_number}]\n{p.text}" for p in pages)
        chunks = [
            ChunkExtraction(
                chunk_index=0,
                page_start=pages[0].page_number,
                page_end=pages[-1].page_number,
                content=full_text,
                token_count=len(full_text.split()),
            )
        ]

    # Map-reduce: if 1 or 2 chunks, direct single-pass reduction; otherwise, map over chunks then reduce
    if len(chunks) <= 2:
        logger.info("document %s has %d chunk(s); using single-pass summarization", document_id, len(chunks))
        combined_content = "\n\n--- Next Section ---\n\n".join(
            f"[Page {c.page_start} - {c.page_end}]\n{c.content}" for c in chunks
        )
        sections_summary = "Full Document Text (Pages 1 to " + str(pages[-1].page_number if pages else 1) + ")"

        reduce_template = load_prompt("summary_reduce_prompt", "v1")
        prompt = reduce_template.format(
            sections_summary=sections_summary,
            findings_text=combined_content,
        )

        summary = await generate_with_retry(
            provider=provider,
            prompt=prompt,
            schema=DocumentSummaryResponse,
            system_prompt=system_prompt,
            temperature=0.1,
        )
    else:
        logger.info("document %s has %d chunks; executing map-reduce summarization", document_id, len(chunks))
        chunk_template = load_prompt("summary_chunk_prompt", "v1")
        chunk_findings: list[ChunkSummaryExtraction] = []

        # Map step: extract partial findings per chunk
        for chunk in chunks:
            chunk_prompt = chunk_template.format(
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                chunk_text=chunk.content,
            )
            try:
                finding = await generate_with_retry(
                    provider=provider,
                    prompt=chunk_prompt,
                    schema=ChunkSummaryExtraction,
                    system_prompt=system_prompt,
                    temperature=0.1,
                )
                chunk_findings.append(finding)
            except Exception as e:
                logger.warning("map step failed for chunk %d: %s. Continuing with remaining chunks.", chunk.chunk_index, e)

        # Consolidate map findings
        aggregated_text_blocks = []
        for i, f in enumerate(chunk_findings):
            block = [f"=== Section {i + 1} ==="]
            if f.parties:
                block.append("Parties: " + "; ".join(f"{p.name} ({p.role})" for p in f.parties))
            if f.conditions:
                block.append("Conditions: " + "; ".join(c.text for c in f.conditions))
            if f.obligations:
                block.append("Obligations: " + "; ".join(f"{o.text} [Quote: \"{o.evidence_quote}\" on p.{o.source_page}]" for o in f.obligations))
            if f.financial_terms:
                block.append("Financial: " + "; ".join(t.text for t in f.financial_terms))
            aggregated_text_blocks.append("\n".join(block))

        findings_summary = "\n\n".join(aggregated_text_blocks)
        sections_overview = f"{len(chunks)} chunks covering {len(pages)} pages"

        reduce_template = load_prompt("summary_reduce_prompt", "v1")
        reduce_prompt = reduce_template.format(
            sections_summary=sections_overview,
            findings_text=findings_summary,
        )

        summary = await generate_with_retry(
            provider=provider,
            prompt=reduce_prompt,
            schema=DocumentSummaryResponse,
            system_prompt=system_prompt,
            temperature=0.1,
        )

    # Grounding & Verification step
    summary = verify_summary_quotes(summary, pages)
    summary.llm_provider = provider.provider_name
    summary.llm_model = provider.model_name

    logger.info(
        "summarization completed for %s: title='%s', verification_rate=%.1f%%",
        document_id,
        summary.title,
        summary.verification_rate,
    )

    return summary

