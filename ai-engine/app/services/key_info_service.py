import logging
from app.prompts import load_prompt
from app.providers.base import LLMProvider
from app.schemas.extraction import PageExtraction
from app.schemas.key_info import (
    FactItem,
    ImportantDateItem,
    KeyInfoRequest,
    KeyInfoResponse,
    RawKeyInfoResult,
)
from app.services.llm_validator import generate_with_retry
from app.services.quote_verifier import verify_quote

logger = logging.getLogger("ai_engine.key_info_service")


def normalize_fact_item(fact: FactItem, pages: list[PageExtraction]) -> FactItem:
    """Normalize fact values, enforcing 'Not specified' and evidence quote verification."""
    raw_val = (fact.value or "").strip()
    if not raw_val or raw_val.lower() in ("not specified", "none", "n/a", "unknown", "null", "-"):
        return FactItem(
            value="Not specified",
            source_page=None,
            evidence_quote=None,
            quote_verified=False,
            provenance="EXTRACTED",
        )

    # If an actual fact value is present, verify evidence quote if provided
    verified = False
    page = fact.source_page
    if fact.evidence_quote:
        verified, matched_page = verify_quote(
            quote=fact.evidence_quote,
            pages=pages,
            claimed_page=fact.source_page,
            threshold=0.88,
        )
        page = matched_page

    return FactItem(
        value=raw_val,
        source_page=page,
        evidence_quote=fact.evidence_quote.strip() if fact.evidence_quote else None,
        quote_verified=verified,
        provenance="EXTRACTED",
    )


async def extract_key_info(
    request: KeyInfoRequest,
    provider: LLMProvider,
) -> KeyInfoResponse:
    """Extract key commercial, financial, and temporal facts with Rule 6 enforcement."""
    page_objs = [
        PageExtraction(
            page_number=p.get("page_number", idx + 1),
            text=p.get("text", ""),
            ocr_used=p.get("ocr_used", False),
        )
        for idx, p in enumerate(request.pages)
    ]

    full_document_content = "\n\n".join(
        f"--- PAGE {p.page_number} ---\n{p.text}" for p in page_objs
    )

    system_prompt = load_prompt("system_prompt", "v1")
    prompt_template = load_prompt("key_info_prompt", "v1")

    prompt = prompt_template.format(document_content=full_document_content)

    logger.info(
        "extracting key information for document %s (pages=%d) via %s",
        request.document_id,
        len(page_objs),
        provider.provider_name,
    )

    raw_result = await generate_with_retry(
        provider=provider,
        prompt=prompt,
        schema=RawKeyInfoResult,
        system_prompt=system_prompt,
        temperature=0.0,
    )

    # Process and normalize all factual fields
    norm_amount = normalize_fact_item(raw_result.contract_amount, page_objs)
    norm_deadlines = normalize_fact_item(raw_result.payment_deadlines, page_objs)
    norm_penalties = normalize_fact_item(raw_result.penalties, page_objs)
    norm_start = normalize_fact_item(raw_result.start_date, page_objs)
    norm_end = normalize_fact_item(raw_result.end_date, page_objs)
    norm_renewal = normalize_fact_item(raw_result.renewal_date, page_objs)
    norm_notice = normalize_fact_item(raw_result.notice_period, page_objs)
    norm_termination = normalize_fact_item(raw_result.termination_conditions, page_objs)

    # Verify quotes on important dates
    verified_dates: list[ImportantDateItem] = []
    for d in raw_result.important_dates:
        d_verified = False
        d_page = d.source_page
        if d.evidence_quote:
            d_verified, d_matched = verify_quote(
                quote=d.evidence_quote,
                pages=page_objs,
                claimed_page=d.source_page,
                threshold=0.88,
            )
            d_page = d_matched

        verified_dates.append(
            ImportantDateItem(
                event=d.event.strip(),
                date_value=d.date_value.strip(),
                source_page=d_page,
                evidence_quote=d.evidence_quote.strip() if d.evidence_quote else None,
                quote_verified=d_verified,
            )
        )

    return KeyInfoResponse(
        document_id=request.document_id,
        contract_amount=norm_amount,
        payment_deadlines=norm_deadlines,
        penalties=norm_penalties,
        start_date=norm_start,
        end_date=norm_end,
        renewal_date=norm_renewal,
        notice_period=norm_notice,
        termination_conditions=norm_termination,
        obligations=[o.strip() for o in raw_result.obligations if o.strip()],
        important_dates=verified_dates,
    )

