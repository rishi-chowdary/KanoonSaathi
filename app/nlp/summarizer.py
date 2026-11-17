import re
from dataclasses import dataclass, field

import numpy as np

from app.nlp.extraction import PageData
from app.nlp.registry import get_sentence_transformer
from app.nlp.segmentation import legal_sentence_tokenizer


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


def generate_extractive_summary(
    full_text: str,
    pages: list[PageData] | None = None,
    document_type: str = "General Contract",
    parties: list[str] | None = None,
) -> StructuredSummaryResult:
    """Generate extractive document summaries using SBERT TextRank + Maximal Marginal Relevance (MMR).

    Hard Invariants:
    - 100% of sentences in summary_short and summary_detailed exist verbatim in full_text.
    - Zero abstractive hallucinations.
    """
    if not full_text.strip():
        return StructuredSummaryResult(
            summary_short="",
            summary_detailed="",
            purpose=f"General legal agreement governing {document_type.lower()} provisions.",
            main_conditions=[],
            obligations_summary=[],
            financial_terms_summary=[],
        )

    page_list = pages or [
        PageData(page_number=1, text=full_text, char_count=len(full_text))
    ]
    raw_sentences = legal_sentence_tokenizer.tokenize(full_text)

    # 1. Candidate Sentence Filtering
    candidates: list[tuple[str, int, int]] = []  # (sentence, char_offset, page_number)
    for sent in raw_sentences:
        clean = sent.strip()
        # Clean leading section number prefix for cleaner prose while preserving substring validity
        clean_stripped = re.sub(
            r"^(?:section\s+\d+[\.\:]?|\d+[\.\:]?)\s*(?:[A-Z][A-Za-z\s]+[\.\:\n]+)?",
            "",
            clean,
            flags=re.IGNORECASE,
        ).strip()
        if len(clean_stripped) >= 30 and clean_stripped in full_text:
            clean = clean_stripped

        # Discard headers, short metadata labels, and signature blocks
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
            for k in ["IN WITNESS WHEREOF", "Date:", "Title:", "By:"]
        ):
            continue

        # Strictly verify exact presence in full_text
        pos = full_text.find(clean)
        if pos >= 0:
            pg = _find_page_for_offset(pos, page_list)
            candidates.append((clean, pos, pg))

    if not candidates:
        # Fallback to first non-empty sentence
        fallback = (
            raw_sentences[0].strip() if raw_sentences else full_text[:120].strip()
        )
        return StructuredSummaryResult(
            summary_short=fallback,
            summary_detailed=fallback,
            purpose=f"Agreement defining terms and conditions for {document_type.lower()}.",
            main_conditions=[],
            obligations_summary=[],
            financial_terms_summary=[],
        )

    # 2. SBERT Dense Embeddings
    model = get_sentence_transformer()
    candidate_texts = [c[0] for c in candidates]
    embs = model.encode(candidate_texts, convert_to_numpy=True)
    if embs.ndim == 1:
        embs = embs.reshape(1, -1)

    # Normalize vectors
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    norm_embs = embs / norms

    # 3. Document Centroid & Centrality Scoring
    centroid = np.mean(norm_embs, axis=0)
    c_norm = np.linalg.norm(centroid)
    if c_norm > 0:
        centroid = centroid / c_norm
    centrality_scores = np.dot(norm_embs, centroid)

    # 4. Maximal Marginal Relevance (MMR) Selection
    # lambda_param = 0.65 balances document centrality with sentence diversity
    lambda_param = 0.65
    selected_indices: list[int] = []

    # Pick top central sentence first
    first_idx = int(np.argmax(centrality_scores))
    selected_indices.append(first_idx)

    max_to_select = min(7, len(candidates))
    while len(selected_indices) < max_to_select:
        remaining_indices = [
            i for i in range(len(candidates)) if i not in selected_indices
        ]
        if not remaining_indices:
            break

        best_mmr = -float("inf")
        best_candidate = remaining_indices[0]

        for cand_idx in remaining_indices:
            cand_vec = norm_embs[cand_idx]
            relevance = centrality_scores[cand_idx]

            # Redundancy: max similarity to already selected sentences
            selected_vecs = norm_embs[selected_indices]
            redundancy = float(np.max(np.dot(selected_vecs, cand_vec)))

            mmr_score = lambda_param * relevance - (1.0 - lambda_param) * redundancy
            if mmr_score > best_mmr:
                best_mmr = mmr_score
                best_candidate = cand_idx

        selected_indices.append(best_candidate)

    # Sort selected sentences in chronological order of appearance in contract
    short_indices = sorted(
        selected_indices[: min(3, len(selected_indices))],
        key=lambda i: candidates[i][1],
    )
    detailed_indices = sorted(selected_indices, key=lambda i: candidates[i][1])

    short_sentences = [candidates[i][0] for i in short_indices]
    detailed_sentences = [candidates[i][0] for i in detailed_indices]

    summary_short = " ".join(short_sentences)
    summary_detailed = "\n\n".join(detailed_sentences)

    # 5. Purpose Synthesis
    parties_str = " and ".join(parties) if parties else "the contracting parties"
    purpose = (
        f"Establishes a legally binding {document_type.lower()} defining rights, obligations, "
        f"and operational conditions between {parties_str}."
    )

    # 6. Structured Summary Sections
    main_conditions: list[dict] = []
    obligations_summary: list[dict] = []
    financial_terms_summary: list[dict] = []

    for text, pos, pg in candidates:
        t_lower = text.lower()
        if any(
            k in t_lower
            for k in [
                "governed by",
                "jurisdiction",
                "terminate",
                "remain in effect",
                "term of",
            ]
        ):
            if len(main_conditions) < 3:
                main_conditions.append(
                    {
                        "text": text,
                        "source_page": pg,
                        "evidence_quote": text,
                        "quote_verified": text in full_text,
                    }
                )
        elif (
            any(
                k in t_lower
                for k in [
                    "shall hold",
                    "shall not",
                    "agrees to employ",
                    "assigns to",
                    "shall maintain",
                ]
            )
            and len(obligations_summary) < 3
        ):
            obligations_summary.append(
                {
                    "text": text,
                    "source_page": pg,
                    "evidence_quote": text,
                    "quote_verified": text in full_text,
                }
            )
        elif (
            any(
                k in t_lower
                for k in [
                    "salary",
                    "rent",
                    "fee",
                    "payment",
                    "installment",
                    "invoice",
                    "deposit",
                ]
            )
            and len(financial_terms_summary) < 3
        ):
            financial_terms_summary.append(
                {
                    "text": text,
                    "source_page": pg,
                    "evidence_quote": text,
                    "quote_verified": text in full_text,
                }
            )

    return StructuredSummaryResult(
        summary_short=summary_short,
        summary_detailed=summary_detailed,
        purpose=purpose,
        main_conditions=main_conditions,
        obligations_summary=obligations_summary,
        financial_terms_summary=financial_terms_summary,
    )
