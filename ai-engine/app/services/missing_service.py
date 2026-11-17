import logging
import os
import re
import yaml
from app.prompts import load_prompt
from app.providers.base import LLMProvider
from app.schemas.extraction import PageExtraction
from app.schemas.missing import (
    MissingProvisionItem,
    MissingProvisionsRequest,
    MissingProvisionsResponse,
    RawMissingAnalysisResult,
)
from app.services.llm_validator import generate_with_retry

logger = logging.getLogger("ai_engine.missing_service")

PROVISIONS_YAML_PATH = os.path.join(
    os.path.dirname(__file__), "..", "analyzers", "expected_provisions.yaml"
)


def load_expected_provisions_checklist() -> dict[str, list[dict]]:
    """Load the curated checklist of standard provisions per document type."""
    try:
        with open(PROVISIONS_YAML_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error("failed to load expected provisions yaml: %s", e)
        return {}


def detect_document_type(text: str, hint: str | None = None) -> str:
    """Classify document type from hints or text signals."""
    if hint:
        h = hint.lower()
        if "employ" in h:
            return "employment"
        if "lease" in h or "rent" in h:
            return "rental_lease"
        if "nda" in h or "non-disclosure" in h or "confidential" in h:
            return "nda"
        if "service" in h or "contractor" in h or "consult" in h:
            return "service_agreement"
        if "sale" in h or "purchase" in h:
            return "sale"
        if "loan" in h or "promissory" in h or "credit" in h or "borrow" in h:
            return "loan"

    norm = text.lower()
    scores = {
        "nda": len(re.findall(r"\b(?:confidential|non-disclosure|disclosing party|receiving party)\b", norm)),
        "employment": len(re.findall(r"\b(?:employee|employer|salary|employment|duties|severance)\b", norm)),
        "rental_lease": len(re.findall(r"\b(?:lease|tenant|landlord|premises|rent|security deposit)\b", norm)),
        "service_agreement": len(re.findall(r"\b(?:services|contractor|deliverables|statement of work|client)\b", norm)),
        "loan": len(re.findall(r"\b(?:borrower|lender|principal amount|promissory note|interest rate)\b", norm)),
        "sale": len(re.findall(r"\b(?:buyer|seller|purchase price|warranty|delivery of goods)\b", norm)),
    }

    best_type, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score >= 3:
        return best_type
    return "other"


async def analyze_missing_provisions(
    request: MissingProvisionsRequest,
    provider: LLMProvider,
) -> MissingProvisionsResponse:
    """Identify missing clauses and potential omissions based on document type checklist and LLM analysis."""
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

    doc_type = detect_document_type(full_document_content, request.document_type_hint)
    all_checklists = load_expected_provisions_checklist()
    checklist = all_checklists.get(doc_type) or all_checklists.get("other", [])

    # Format checklist for the prompt
    checklist_lines = []
    for item in checklist:
        checklist_lines.append(
            f"- [{item.get('category')}] {item.get('title')}: {item.get('why_it_matters')} (Risk: {item.get('risk_level')})"
        )
    checklist_str = "\n".join(checklist_lines)

    system_prompt = load_prompt("system_prompt", "v1")
    prompt_template = load_prompt("missing_analysis_prompt", "v1")

    prompt = prompt_template.format(
        document_type=doc_type.replace("_", " ").title(),
        expected_checklist=checklist_str,
        document_content=full_document_content,
    )

    logger.info(
        "analyzing missing provisions for doc %s (type=%s, checklist_items=%d) via %s",
        request.document_id,
        doc_type,
        len(checklist),
        provider.provider_name,
    )

    llm_result = await generate_with_retry(
        provider=provider,
        prompt=prompt,
        schema=RawMissingAnalysisResult,
        system_prompt=system_prompt,
        temperature=0.1,
    )

    # Process and enforce Rule 7 labels
    processed_items: list[MissingProvisionItem] = []
    for item in llm_result.missing_provisions:
        # Enforce exact standard label
        processed_items.append(
            MissingProvisionItem(
                category=item.category.strip(),
                clause_name=item.clause_name.strip(),
                why_it_matters=item.why_it_matters.strip(),
                typical_provision=item.typical_provision.strip(),
                risk_level=item.risk_level,
                label="Possible omission",
            )
        )

    return MissingProvisionsResponse(
        document_id=request.document_id,
        detected_document_type=doc_type,
        missing_provisions=processed_items,
        total_missing=len(processed_items),
        disclaimer=(
            "Legal Disclaimer: LexiLegal AI provides automated analysis aid. "
            "Missing clause notices are labeled 'Possible omission' and do not constitute formal legal counsel."
        ),
    )

