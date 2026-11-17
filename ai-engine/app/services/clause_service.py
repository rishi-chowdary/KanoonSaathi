import difflib
import logging
import re
from app.prompts import load_prompt
from app.providers.base import LLMProvider
from app.schemas.clause import (
    BatchExplanationsResponse,
    ChunkClauseExtraction,
    ClauseAnalysisResponse,
    ClauseExplanations,
    ClauseItem,
    RawClauseItem,
    STANDARD_CLAUSE_CATEGORIES,
)
from app.schemas.extraction import ChunkExtraction, PageExtraction
from app.services.llm_validator import generate_with_retry
from app.services.quote_verifier import normalize_text, verify_quote

logger = logging.getLogger("ai_engine.clause_service")

DATE_MONTH_REGEX = re.compile(
    r"\b(?:january|february|march|april|june|july|august|september|october|november|december)\b",
    re.IGNORECASE,
)
MAY_DATE_REGEX = re.compile(
    r"\bMay\s+(?:\d{1,2}(?:st|nd|rd|th)?|\d{4})\b|\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?May)\b"
)
NUMBER_REGEX = re.compile(r"\b(?:\$|€|£)?\d+(?:,\d+)*(?:\.\d+)?%?\b")


def validate_numbers_and_dates(
    original_text: str, explanations: dict[str, str]
) -> tuple[bool, list[str]]:
    """Validate that explanations do not introduce numbers or dates absent from original text."""
    if not original_text:
        return True, []

    norm_original = normalize_text(original_text)
    warnings: list[str] = []
    is_verified = True

    for mode, text in explanations.items():
        if not text:
            continue

        # Check numbers and currency / percentage amounts
        found_numbers = NUMBER_REGEX.findall(text)
        for num in found_numbers:
            clean_num = num.strip("$€£%,. ")
            # Ignore standalone single digits (1, 2, 3) which often appear in bullet lists or formatting
            if len(clean_num) == 1 and clean_num.isdigit():
                continue
            if clean_num and clean_num not in norm_original:
                is_verified = False
                warnings.append(
                    f"Number '{num}' in {mode} explanation was not found in original clause text"
                )

        # Check explicit month dates (excluding modal verb 'may' unless accompanied by date digits)
        found_months = DATE_MONTH_REGEX.findall(text)
        if MAY_DATE_REGEX.search(text):
            found_months.append("May")

        for month in found_months:
            if month.lower() not in norm_original:
                is_verified = False
                warnings.append(
                    f"Month '{month}' in {mode} explanation was not found in original clause text"
                )

    return is_verified, warnings


def is_duplicate_clause(a: RawClauseItem, b: RawClauseItem) -> bool:
    """Determine whether two extracted clauses from overlapping chunks represent the same clause."""
    # Matching explicit section reference
    if (
        a.section_reference
        and b.section_reference
        and normalize_text(a.section_reference) == normalize_text(b.section_reference)
    ):
        return True

    # Matching title and category
    if normalize_text(a.title) == normalize_text(b.title) and a.category == b.category:
        return True

    # High text similarity on original text or evidence quote
    norm_a = normalize_text(a.original_text)
    norm_b = normalize_text(b.original_text)
    if norm_a and norm_b:
        ratio = difflib.SequenceMatcher(None, norm_a, norm_b).ratio()
        if ratio >= 0.75:
            return True
        if len(norm_a) > 40 and (norm_a in norm_b or norm_b in norm_a):
            return True

    norm_qa = normalize_text(a.evidence_quote)
    norm_qb = normalize_text(b.evidence_quote)
    if norm_qa and norm_qb and len(norm_qa) > 20:
        if norm_qa in norm_qb or norm_qb in norm_qa:
            return True

    return False


def merge_clauses(target: RawClauseItem, incoming: RawClauseItem) -> RawClauseItem:
    """Merge incoming duplicate into target, keeping the most complete information."""
    if len(incoming.original_text or "") > len(target.original_text or ""):
        target.original_text = incoming.original_text

    if not target.section_reference and incoming.section_reference:
        target.section_reference = incoming.section_reference

    # Prefer earlier source page
    target.source_page = min(target.source_page, incoming.source_page)

    # Prefer higher importance
    importance_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    if importance_rank.get(incoming.importance, 1) > importance_rank.get(target.importance, 1):
        target.importance = incoming.importance

    return target


async def analyze_document_clauses(
    document_id: str,
    pages: list[PageExtraction],
    chunks: list[ChunkExtraction],
    provider: LLMProvider,
) -> ClauseAnalysisResponse:
    """Two-pass clause extraction pipeline:
    Pass 1: Per-chunk extraction with 17 categories + Other, followed by chunk overlap deduplication.
    Pass 2: Batch generation of 3 explanation modes, number/date validation, and quote verification.
    """
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

    if not chunks:
        return ClauseAnalysisResponse(
            document_id=document_id,
            clauses=[],
            total_clauses=0,
            verification_rate=0.0,
            llm_provider=provider.provider_name,
            llm_model=provider.model_name,
            warnings=["No document text available for clause analysis."],
        )

    # --- PASS 1: Extraction per chunk ---
    logger.info("clause extraction Pass 1: extracting from %d chunk(s)", len(chunks))
    chunk_prompt_template = load_prompt("clause_chunk_prompt", "v1")
    raw_clauses: list[RawClauseItem] = []

    for chunk in chunks:
        prompt = chunk_prompt_template.format(
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            chunk_text=chunk.content,
        )
        try:
            extraction = await generate_with_retry(
                provider=provider,
                prompt=prompt,
                schema=ChunkClauseExtraction,
                system_prompt=system_prompt,
                temperature=0.1,
            )
            for c in extraction.clauses:
                # Normalize category to standard set or Other
                if c.category not in STANDARD_CLAUSE_CATEGORIES:
                    if not c.custom_label:
                        c.custom_label = c.category
                    c.category = "Other"
                raw_clauses.append(c)
        except Exception as e:
            logger.warning(
                "clause extraction failed for chunk %d: %s. Continuing with next chunk.",
                chunk.chunk_index,
                e,
            )

    # Deduplicate across chunks
    unique_clauses: list[RawClauseItem] = []
    for candidate in raw_clauses:
        matched = False
        for existing in unique_clauses:
            if is_duplicate_clause(existing, candidate):
                merge_clauses(existing, candidate)
                matched = True
                break
        if not matched:
            unique_clauses.append(candidate)

    logger.info(
        "Pass 1 finished: extracted %d raw clauses, deduplicated to %d unique clauses",
        len(raw_clauses),
        len(unique_clauses),
    )

    if not unique_clauses:
        return ClauseAnalysisResponse(
            document_id=document_id,
            clauses=[],
            total_clauses=0,
            verification_rate=0.0,
            llm_provider=provider.provider_name,
            llm_model=provider.model_name,
            warnings=["No clauses could be extracted from the document."],
        )

    # --- PASS 2: Batch Simplification & 3-mode Explanations ---
    logger.info("clause extraction Pass 2: generating 3 explanation modes in batches")
    simplify_prompt_template = load_prompt("clause_simplify_prompt", "v1")
    explanations_map: dict[int, ClauseExplanations] = {}

    batch_size = 4
    for batch_start in range(0, len(unique_clauses), batch_size):
        batch = unique_clauses[batch_start : batch_start + batch_size]
        batch_text_lines = []
        for idx, clause in enumerate(batch):
            batch_text_lines.append(
                f"[clause_index: {idx}]\n"
                f"Title: {clause.title}\n"
                f"Category: {clause.category}\n"
                f"Original Text: {clause.original_text}\n"
            )
        clauses_text = "\n---\n".join(batch_text_lines)
        prompt = simplify_prompt_template.format(clauses_text=clauses_text)

        try:
            batch_resp = await generate_with_retry(
                provider=provider,
                prompt=prompt,
                schema=BatchExplanationsResponse,
                system_prompt=system_prompt,
                temperature=0.2,
            )
            for exp in batch_resp.explanations:
                global_idx = batch_start + exp.clause_index
                if global_idx < len(unique_clauses):
                    explanations_map[global_idx] = exp
        except Exception as e:
            logger.warning(
                "batch simplification failed for clauses %d-%d: %s. Using fallbacks.",
                batch_start,
                batch_start + len(batch),
                e,
            )

    # --- Post-Check Validation & Grounding ---
    final_clauses: list[ClauseItem] = []
    verified_quote_count = 0

    for idx, clause in enumerate(unique_clauses):
        exp = explanations_map.get(idx)
        if exp:
            simple = exp.simplified_simple
            detailed = exp.simplified_detailed
            professional = exp.simplified_professional
        else:
            simple = f"This clause sets forth terms regarding {clause.title.lower()}."
            detailed = f"Under this provision, {clause.affected_party} is subject to the following obligations: {clause.original_text[:200]}..."
            professional = f"Governs {clause.category.lower()} requirements and associated liabilities for {clause.affected_party}."

        # Number and date post-check validation
        explanations_dict = {
            "simple": simple,
            "detailed": detailed,
            "professional": professional,
        }
        num_dates_ok, hallucination_warnings = validate_numbers_and_dates(
            clause.original_text, explanations_dict
        )

        # Quote verification against document pages
        quote_ok, verified_page = verify_quote(
            clause.evidence_quote, pages, claimed_page=clause.source_page
        )
        if quote_ok:
            verified_quote_count += 1
            clause.source_page = verified_page

        item = ClauseItem(
            title=clause.title,
            category=clause.category,
            custom_label=clause.custom_label,
            original_text=clause.original_text,
            simplified_simple=simple,
            simplified_detailed=detailed,
            simplified_professional=professional,
            importance=clause.importance,
            affected_party=clause.affected_party,
            source_page=clause.source_page,
            section_reference=clause.section_reference,
            evidence_quote=clause.evidence_quote,
            quote_verified=quote_ok,
            provenance="EXTRACTED",
            numbers_dates_verified=num_dates_ok,
            warnings=hallucination_warnings,
        )
        final_clauses.append(item)

    verification_rate = (
        round((verified_quote_count / len(final_clauses)) * 100.0, 2)
        if final_clauses
        else 0.0
    )

    logger.info(
        "clause analysis finished for %s: %d clauses, verification rate %.1f%%",
        document_id,
        len(final_clauses),
        verification_rate,
    )

    return ClauseAnalysisResponse(
        document_id=document_id,
        clauses=final_clauses,
        total_clauses=len(final_clauses),
        verification_rate=verification_rate,
        llm_provider=provider.provider_name,
        llm_model=provider.model_name,
        warnings=[],
    )

