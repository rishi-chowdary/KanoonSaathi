import logging
import re
from app.prompts import load_prompt
from app.providers.base import LLMProvider
from app.schemas.extraction import PageExtraction
from app.schemas.risk import (
    RawRiskItem,
    RiskAnalysisRequest,
    RiskAnalysisResponse,
    RiskFindingItem,
)
from app.services.llm_validator import generate_with_retry
from app.services.quote_verifier import verify_quote
from pydantic import BaseModel, Field

logger = logging.getLogger("ai_engine.risk_service")

# Rule 7: Banned legal conclusions and their compliant replacements
FORBIDDEN_RULE7_PATTERNS = [
    (re.compile(r"\b(?:is|are)\s+illegal\b", re.IGNORECASE), "may face legal enforceability issues"),
    (re.compile(r"\billegal\b", re.IGNORECASE), "potentially unfavorable"),
    (re.compile(r"\bnull\s+and\s+void\b", re.IGNORECASE), "subject to validity scrutiny"),
    (re.compile(r"\b(?:is|are)\s+void\b", re.IGNORECASE), "may face validity challenges"),
    (re.compile(r"\bvoid\b", re.IGNORECASE), "potentially non-standard"),
    (re.compile(r"\b(?:is|are)\s+unenforceable\b", re.IGNORECASE), "may carry significant enforceability risk"),
    (re.compile(r"\bunenforceable\b", re.IGNORECASE), "challenging to enforce under certain laws"),
    (re.compile(r"\bunlawful\b", re.IGNORECASE), "legally questionable"),
    (re.compile(r"\bviolates\s+(?:the\s+)?law\b", re.IGNORECASE), "may not align with standard statutory protections"),
    (re.compile(r"\bcontrary\s+to\s+public\s+policy\b", re.IGNORECASE), "may face judicial resistance"),
]

GOVERNING_LAW_REGEX = re.compile(
    r"\b(?:governed by|governing law|laws of (?:the state of|the commonwealth of)?|jurisdiction of)\b",
    re.IGNORECASE,
)

JURISDICTION_CAVEAT_TEXT = (
    "Governing law is not explicitly specified in this agreement. The legal risk profile and "
    "enforceability of this provision may vary substantially depending on applicable state or local jurisdiction."
)


def filter_rule7_language(text: str) -> str:
    """Enforce Rule 7 by replacing forbidden legal conclusion phrases with compliant language."""
    if not text:
        return text
    sanitized = text
    for pattern, replacement in FORBIDDEN_RULE7_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


class LLMRisksWrapper(BaseModel):
    risks: list[RawRiskItem] = Field(default_factory=list)


async def analyze_risks(
    request: RiskAnalysisRequest,
    provider: LLMProvider,
) -> RiskAnalysisResponse:
    """Extract and evaluate risk findings across 6 categories and 4 levels with Rule 7 post-filtering,
    quote verification, and jurisdiction caveats.
    """
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

    # Check whether governing law is present in the document
    governing_law_found = request.governing_law_found
    if governing_law_found is None:
        governing_law_found = bool(GOVERNING_LAW_REGEX.search(full_document_content))

    system_prompt = load_prompt("system_prompt", "v1")
    prompt_template = load_prompt("risk_analysis_prompt", "v1")

    prompt = prompt_template.format(document_content=full_document_content)

    logger.info(
        "analyzing risks for document %s (pages=%d, governing_law_found=%s) via %s",
        request.document_id,
        len(page_objs),
        governing_law_found,
        provider.provider_name,
    )

    llm_result = await generate_with_retry(
        provider=provider,
        prompt=prompt,
        schema=LLMRisksWrapper,
        system_prompt=system_prompt,
        temperature=0.1,
    )

    processed_risks: list[RiskFindingItem] = []
    high_count = 0
    med_count = 0
    low_count = 0
    info_count = 0

    for r in llm_result.risks:
        # 1. Enforce Rule 7 post-filter on explanation, why_it_matters, and possible_consequences
        clean_exp = filter_rule7_language(r.explanation)
        clean_why = filter_rule7_language(r.why_it_matters)
        clean_consequences = filter_rule7_language(r.possible_consequences)
        clean_questions = [filter_rule7_language(q) for q in r.suggested_questions]

        # 2. Verify evidence quote
        verified, matched_page = verify_quote(
            quote=r.evidence_quote,
            pages=page_objs,
            claimed_page=r.source_page,
            threshold=0.88,
        )

        # 3. Attach jurisdiction caveat if governing law is unknown
        caveat = None if governing_law_found else JURISDICTION_CAVEAT_TEXT

        # Normalize severity level casing
        level_upper = r.level.upper()
        if level_upper not in ("HIGH", "MEDIUM", "LOW", "INFORMATIONAL"):
            level_upper = "MEDIUM"

        if level_upper == "HIGH":
            high_count += 1
        elif level_upper == "MEDIUM":
            med_count += 1
        elif level_upper == "LOW":
            low_count += 1
        else:
            info_count += 1

        finding = RiskFindingItem(
            title=r.title.strip(),
            category=r.category,
            level=level_upper,  # type: ignore
            original_clause=r.original_clause.strip(),
            evidence_quote=r.evidence_quote.strip(),
            source_page=matched_page,
            quote_verified=verified,
            explanation=clean_exp,
            why_it_matters=clean_why,
            possible_consequences=clean_consequences,
            suggested_questions=clean_questions,
            jurisdiction_caveat=caveat,
            provenance="AI_INTERPRETATION",
        )
        processed_risks.append(finding)

    # Compute composite risk score (0 to 10 scale)
    total = len(processed_risks)
    weighted_score = (high_count * 3.0 + med_count * 1.5 + low_count * 0.5)
    overall_score = min(round(weighted_score / max(total, 1) * 3.33, 1), 10.0) if total > 0 else 0.0

    return RiskAnalysisResponse(
        document_id=request.document_id,
        risks=processed_risks,
        total_risks=total,
        high_risks=high_count,
        medium_risks=med_count,
        low_risks=low_count,
        informational_risks=info_count,
        governing_law_found=governing_law_found,
        jurisdiction_warning=None if governing_law_found else JURISDICTION_CAVEAT_TEXT,
        overall_risk_score=overall_score,
    )

