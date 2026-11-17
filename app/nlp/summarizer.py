import re
from dataclasses import dataclass, field

import numpy as np

from app.nlp.extraction import PageData
from app.nlp.registry import get_sentence_transformer
from app.nlp.segmentation import legal_sentence_tokenizer

_CONDITION_HINTS = (
    "governed by",
    "jurisdiction",
    "terminate",
    "remain in effect",
    "term of",
)
_OBLIGATION_HINTS = (
    "shall hold",
    "shall not",
    "agrees to employ",
    "assigns to",
    "shall maintain",
)
_FINANCIAL_HINTS = (
    "salary",
    "rent",
    "fee",
    "payment",
    "installment",
    "invoice",
    "deposit",
)


@dataclass
class StructuredSummaryResult:
    summary_short: str
    summary_detailed: str
    purpose: str
    main_conditions: list[dict] = field(default_factory=list)
    obligations_summary: list[dict] = field(default_factory=list)
    financial_terms_summary: list[dict] = field(default_factory=list)


def _find_page_for_offset(offset: int, pages: list[PageData]) -> int:
    if not pages:
        return 1
    running = 0
    for p in pages:
        page_len = len(p.text) + 2
        if running <= offset < running + page_len:
            return p.page_number
        running += page_len
    return pages[-1].page_number


def _filter_candidate_sentences(
    raw_sentences: list[str], full_text: str, page_list: list[PageData]
) -> list[tuple[str, int, int]]:
    candidates: list[tuple[str, int, int]] = []
    for sent in raw_sentences:
        clean = sent.strip()
        stripped = re.sub(
            r"^(?:section\s+\d+[\.\:]?|\d+[\.\:]?)\s*(?:[A-Z][A-Za-z\s]+[\.\:\n]+)?",
            "",
            clean,
            flags=re.IGNORECASE,
        ).strip()
        if len(stripped) >= 30 and stripped in full_text:
            clean = stripped

        if len(clean) < 30 or len(clean) > 500:
            continue
        if (
            clean.startswith("Section ")
            and len(clean.split("\n")) <= 2
            and len(clean) < 80
        ):
            continue
        if any(
            clean.startswith(k)
            for k in ("IN WITNESS WHEREOF", "Date:", "Title:", "By:")
        ):
            continue

        pos = full_text.find(clean)
        if pos >= 0:
            candidates.append((clean, pos, _find_page_for_offset(pos, page_list)))
    return candidates


def _select_mmr_indices(candidate_texts: list[str], max_count: int = 7) -> list[int]:
    model = get_sentence_transformer()
    embs = model.encode(candidate_texts, convert_to_numpy=True)
    if embs.ndim == 1:
        embs = embs.reshape(1, -1)

    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    norm_embs = embs / norms

    centroid = np.mean(norm_embs, axis=0)
    c_norm = np.linalg.norm(centroid)
    if c_norm > 0:
        centroid = centroid / c_norm
    centrality = np.dot(norm_embs, centroid)

    # 0.65 balances document centrality against sentence diversity
    lambda_param = 0.65
    selected: list[int] = [int(np.argmax(centrality))]
    limit = min(max_count, len(candidate_texts))

    while len(selected) < limit:
        remaining = [i for i in range(len(candidate_texts)) if i not in selected]
        if not remaining:
            break
        selected_vecs = norm_embs[selected]
        best_idx = max(
            remaining,
            key=lambda idx: lambda_param * centrality[idx]
            - (1.0 - lambda_param)
            * float(np.max(np.dot(selected_vecs, norm_embs[idx]))),
        )
        selected.append(best_idx)
    return selected


def _build_structured_highlights(
    candidates: list[tuple[str, int, int]], full_text: str
) -> tuple[list[dict], list[dict], list[dict]]:
    main_conditions: list[dict] = []
    obligations: list[dict] = []
    financials: list[dict] = []

    for text, _pos, pg in candidates:
        entry = {
            "text": text,
            "source_page": pg,
            "evidence_quote": text,
            "quote_verified": text in full_text,
        }
        t_lower = text.lower()
        if any(k in t_lower for k in _CONDITION_HINTS):
            if len(main_conditions) < 3:
                main_conditions.append(entry)
        elif any(k in t_lower for k in _OBLIGATION_HINTS) and len(obligations) < 3:
            obligations.append(entry)
        elif any(k in t_lower for k in _FINANCIAL_HINTS) and len(financials) < 3:
            financials.append(entry)

    return main_conditions, obligations, financials


def generate_extractive_summary(
    full_text: str,
    pages: list[PageData] | None = None,
    document_type: str = "General Contract",
    parties: list[str] | None = None,
) -> StructuredSummaryResult:
    """Build short and detailed extractive summaries using SBERT centrality and MMR."""
    if not full_text.strip():
        return StructuredSummaryResult(
            summary_short="",
            summary_detailed="",
            purpose=f"General legal agreement governing {document_type.lower()} provisions.",
        )

    page_list = pages or [
        PageData(page_number=1, text=full_text, char_count=len(full_text))
    ]
    raw_sentences = legal_sentence_tokenizer.tokenize(full_text)
    candidates = _filter_candidate_sentences(raw_sentences, full_text, page_list)

    if not candidates:
        fallback = (
            raw_sentences[0].strip() if raw_sentences else full_text[:120].strip()
        )
        return StructuredSummaryResult(
            summary_short=fallback,
            summary_detailed=fallback,
            purpose=f"Agreement defining terms and conditions for {document_type.lower()}.",
        )

    selected_indices = _select_mmr_indices([c[0] for c in candidates], max_count=7)
    short_indices = sorted(
        selected_indices[: min(3, len(selected_indices))],
        key=lambda i: candidates[i][1],
    )
    detailed_indices = sorted(selected_indices, key=lambda i: candidates[i][1])

    parties_str = " and ".join(parties) if parties else "the contracting parties"
    purpose = (
        f"Establishes a legally binding {document_type.lower()} defining rights, obligations, "
        f"and operational conditions between {parties_str}."
    )
    main_conditions, obligations, financials = _build_structured_highlights(
        candidates, full_text
    )

    return StructuredSummaryResult(
        summary_short=" ".join(candidates[i][0] for i in short_indices),
        summary_detailed="\n\n".join(candidates[i][0] for i in detailed_indices),
        purpose=purpose,
        main_conditions=main_conditions,
        obligations_summary=obligations,
        financial_terms_summary=financials,
    )
