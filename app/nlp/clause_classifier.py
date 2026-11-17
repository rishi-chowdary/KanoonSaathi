import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from app.nlp.registry import get_clause_hf_classifier, get_sentence_transformer

logger = logging.getLogger("lexilegal.nlp.classifier")

# 18 Standard Clause Categories
STANDARD_CATEGORIES = [
    "Confidentiality",
    "Termination",
    "Intellectual Property",
    "Liability and Indemnification",
    "Dispute Resolution",
    "Governing Law",
    "Payment Terms",
    "Representations and Warranties",
    "Non-Compete and Non-Solicitation",
    "Force Majeure",
    "Assignment",
    "Severability",
    "Amendment",
    "Notices",
    "Term and Renewal",
    "Data Protection and Privacy",
    "Insurance",
    "Other",
]

_rules_data: dict[str, Any] | None = None
_prototypes_dict: dict[str, np.ndarray] | None = None
_logged_fallback = False


def _load_rules() -> dict[str, Any]:
    global _rules_data
    if _rules_data is not None:
        return _rules_data

    path = Path("data/clause_rules.yaml")
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        _rules_data = yaml.safe_load(f).get("rules", {})
    return _rules_data


def _load_prototypes() -> dict[str, np.ndarray]:
    global _prototypes_dict
    if _prototypes_dict is not None:
        return _prototypes_dict

    path = Path("data/clause_prototypes.yaml")
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        raw_prototypes = yaml.safe_load(f)

    categories = raw_prototypes.get("categories", {})
    model = get_sentence_transformer()

    embedded: dict[str, np.ndarray] = {}
    for cat, texts in categories.items():
        if texts:
            vecs = model.encode(texts, convert_to_numpy=True)
            if vecs.ndim == 1:
                vecs = vecs.reshape(1, -1)
            mean_vec = np.mean(vecs, axis=0)
            norm = np.linalg.norm(mean_vec)
            if norm > 0:
                mean_vec = mean_vec / norm
            embedded[cat] = mean_vec

    _prototypes_dict = embedded
    return _prototypes_dict


def _rule_score(title: str, text: str) -> dict[str, float]:
    """Compute rule-based keyword match scores for each standard category."""
    rules = _load_rules()
    title_lower = title.lower()
    text_lower = text.lower()[:1500]

    scores: dict[str, float] = {cat: 0.0 for cat in STANDARD_CATEGORIES}

    for cat, rule in rules.items():
        score = 0.0
        # Title matches carry the highest structural signal
        for kw in rule.get("title_keywords", []):
            if kw in title_lower:
                score += 3.5

        # Body keywords provide semantic confirmation
        body_hits = 0
        for kw in rule.get("body_keywords", []):
            if kw in text_lower:
                body_hits += 1
        score += min(2.5, body_hits * 0.8)

        scores[cat] = score

    # Normalize to [0, 1]
    max_val = max(scores.values()) if scores else 0.0
    if max_val > 0:
        return {cat: val / max_val for cat, val in scores.items()}
    return scores


def _sbert_score(title: str, text: str) -> dict[str, float]:
    """Compute SBERT cosine similarity scores against prototype representations."""
    prototypes = _load_prototypes()
    if not prototypes:
        return {cat: 0.0 for cat in STANDARD_CATEGORIES}

    model = get_sentence_transformer()
    clause_sample = f"{title}. {text[:500]}"
    query_vec = model.encode([clause_sample], convert_to_numpy=True)[0]
    query_norm = np.linalg.norm(query_vec)
    if query_norm > 0:
        query_vec = query_vec / query_norm

    sims: dict[str, float] = {}
    for cat in STANDARD_CATEGORIES:
        if cat in prototypes:
            cos = float(np.dot(query_vec, prototypes[cat]))
            sims[cat] = max(0.0, cos)
        else:
            sims[cat] = 0.0

    # Softmax / temperature scaling over positive similarities
    max_sim = max(sims.values()) if sims else 0.0
    if max_sim > 0:
        return {cat: val / max_sim for cat, val in sims.items()}
    return sims


def _hf_score(title: str, text: str) -> dict[str, float] | None:
    """Compute classification probabilities with fine-tuned Hugging Face model if available."""
    model, tokenizer = get_clause_hf_classifier()
    if model is None or tokenizer is None:
        return None

    import torch

    inputs = tokenizer(
        f"{title}: {text[:512]}",
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=True,
    )
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1).squeeze(0).tolist()

    id2label = model.config.id2label
    scores = {cat: 0.0 for cat in STANDARD_CATEGORIES}
    for idx, prob in enumerate(probs):
        label = id2label.get(idx)
        if label in scores:
            scores[label] = float(prob)
    return scores


def classify_clause(
    title: str,
    original_text: str,
    section_reference: str | None = None,
) -> tuple[str, str | None, float, dict[str, float]]:
    """Classify a legal clause using an ensemble of Rules, SBERT Prototypes, and DistilBERT.

    Returns:
        tuple: (category, custom_label, confidence, category_scores)
    """
    global _logged_fallback
    rule_scores = _rule_score(title, original_text)
    sbert_scores = _sbert_score(title, original_text)
    hf_scores = _hf_score(title, original_text)

    # 1. Preamble and Recitals check
    title_norm = title.lower().strip()
    if any(k in title_norm for k in ["preamble", "recital", "witnesseth"]):
        return "Other", "Preamble and Recitals", 0.95, {"Other": 1.0}

    # 2. Check for explicit "Other" clauses (e.g., Definitions, Position/Scope, Maintenance)
    if "definitions" in title_norm or "definition of" in title_norm:
        return "Other", "Definitions", 0.90, {"Other": 0.9}
    if "position and scope" in title_norm or "scope of duties" in title_norm:
        return "Other", "Position and Scope of Duties", 0.90, {"Other": 0.9}
    if "scope of services" in title_norm or "services and scope" in title_norm:
        return "Other", "Scope of Services", 0.90, {"Other": 0.9}
    if "exhibit" in title_norm or "schedule a" in title_norm:
        return "Other", "Exhibit / Schedule", 0.85, {"Other": 0.85}
    if "maintenance" in title_norm and "rent" not in title_norm:
        return "Other", "Maintenance and Alterations", 0.85, {"Other": 0.85}
    if "property description" in title_norm:
        return "Other", "Property Description", 0.90, {"Other": 0.9}

    # 3. Combine model probabilities
    ensemble_scores: dict[str, float] = {}
    if hf_scores is not None:
        # Full 3-component ensemble: 0.40 DistilBERT + 0.35 SBERT + 0.25 Rules
        for cat in STANDARD_CATEGORIES:
            ensemble_scores[cat] = (
                0.40 * hf_scores.get(cat, 0.0)
                + 0.35 * sbert_scores.get(cat, 0.0)
                + 0.25 * rule_scores.get(cat, 0.0)
            )
    else:
        # Fallback 2-component ensemble: 0.55 SBERT + 0.45 Rules
        if not _logged_fallback:
            logger.info(
                "Fine-tuned DistilBERT checkpoint not present in models/clause_classifier. "
                "Executing transparent fallback: SBERT (0.55) + Rule Matcher (0.45)."
            )
            _logged_fallback = True

        for cat in STANDARD_CATEGORIES:
            ensemble_scores[cat] = 0.55 * sbert_scores.get(
                cat, 0.0
            ) + 0.45 * rule_scores.get(cat, 0.0)

    # Clean title heuristics: Title keyword match strongly anchors specific standard categories
    # E.g., "Term and Termination" should prefer "Term and Renewal" or "Termination"
    if "term and termination" in title_norm or "term and renewal" in title_norm:
        ensemble_scores["Term and Renewal"] += 0.4
    elif "non-disclosure" in title_norm or "confidentiality" in title_norm:
        ensemble_scores["Confidentiality"] += 0.5
    elif "non-compete" in title_norm or "non-solicitation" in title_norm:
        ensemble_scores["Non-Compete and Non-Solicitation"] += 0.5
    elif "governing law" in title_norm or "applicable law" in title_norm:
        ensemble_scores["Governing Law"] += 0.5
    elif "indemnif" in title_norm or "limitation of liability" in title_norm:
        ensemble_scores["Liability and Indemnification"] += 0.5
    elif "ip assignment" in title_norm or "intellectual property" in title_norm:
        ensemble_scores["Intellectual Property"] += 0.5
    elif (
        "rent" in title_norm
        or "compensation" in title_norm
        or "payment" in title_norm
        or "fees" in title_norm
    ):
        ensemble_scores["Payment Terms"] += 0.5

    best_cat = max(ensemble_scores, key=ensemble_scores.get)
    best_score = ensemble_scores[best_cat]

    # If confidence is low or category is Other, produce clean custom label
    custom_label = None
    if best_cat == "Other" or best_score < 0.25:
        best_cat = "Other"
        # Generate custom label from title
        clean_title = re.sub(
            r"^(?:section|clause|art\.?|article|\d+[\.\)]?)\s*",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()
        custom_label = clean_title if clean_title else "Miscellaneous"

    return best_cat, custom_label, round(float(best_score), 4), ensemble_scores
