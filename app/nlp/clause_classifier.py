import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from app.nlp.registry import get_clause_hf_classifier, get_sentence_transformer

logger = logging.getLogger("lexilegal.nlp.classifier")

# Standard Contract & Indian Statute Categories
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
    "Criminal Offence and Punishment",
    "Constitutional Right and Provision",
    "Statutory Definition and Exception",
    "Jurisdiction and Procedure",
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

    max_val = max(scores.values()) if scores else 0.0
    if max_val > 0:
        return {cat: val / max_val for cat, val in scores.items()}
    return scores


def _sbert_score(title: str, text: str) -> dict[str, float]:
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


_TITLE_BOOSTS = [
    (("term and termination", "term and renewal"), "Term and Renewal", 0.4),
    (("non-disclosure", "confidentiality"), "Confidentiality", 0.5),
    (("non-compete", "non-solicitation"), "Non-Compete and Non-Solicitation", 0.5),
    (("governing law", "applicable law"), "Governing Law", 0.5),
    (("indemnif", "limitation of liability"), "Liability and Indemnification", 0.5),
    (("ip assignment", "intellectual property"), "Intellectual Property", 0.5),
    (("rent", "compensation", "payment", "fees"), "Payment Terms", 0.5),
]


def _match_explicit_other(
    title_norm: str,
) -> tuple[str, str, float, dict[str, float]] | None:
    if any(k in title_norm for k in ("preamble", "recital", "witnesseth")):
        return "Other", "Preamble and Recitals", 0.95, {"Other": 1.0}
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
    return None


def _combine_scores(
    rule_scores: dict[str, float],
    sbert_scores: dict[str, float],
    hf_scores: dict[str, float] | None,
) -> dict[str, float]:
    global _logged_fallback
    if hf_scores is not None:
        return {
            cat: (
                0.40 * hf_scores.get(cat, 0.0)
                + 0.35 * sbert_scores.get(cat, 0.0)
                + 0.25 * rule_scores.get(cat, 0.0)
            )
            for cat in STANDARD_CATEGORIES
        }

    if not _logged_fallback:
        logger.info(
            "fine-tuned classifier not found in models/clause_classifier; using sbert (0.55) + rules (0.45)"
        )
        _logged_fallback = True

    return {
        cat: 0.55 * sbert_scores.get(cat, 0.0) + 0.45 * rule_scores.get(cat, 0.0)
        for cat in STANDARD_CATEGORIES
    }


def _apply_title_boosts(title_norm: str, scores: dict[str, float]) -> None:
    for keywords, category, boost in _TITLE_BOOSTS:
        if any(k in title_norm for k in keywords):
            scores[category] += boost
            return


def classify_clause(
    title: str,
    original_text: str,
    section_reference: str | None = None,
) -> tuple[str, str | None, float, dict[str, float]]:
    """Classify a clause with the rule, SBERT, and optional DistilBERT ensemble."""
    title_norm = title.lower().strip()
    explicit_other = _match_explicit_other(title_norm)
    if explicit_other is not None:
        return explicit_other

    ensemble_scores = _combine_scores(
        _rule_score(title, original_text),
        _sbert_score(title, original_text),
        _hf_score(title, original_text),
    )
    _apply_title_boosts(title_norm, ensemble_scores)

    best_cat = max(ensemble_scores, key=ensemble_scores.get)
    best_score = ensemble_scores[best_cat]

    custom_label = None
    if best_cat == "Other" or best_score < 0.25:
        best_cat = "Other"
        clean_title = re.sub(
            r"^(?:section|clause|art\.?|article|\d+[\.\)]?)\s*",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()
        custom_label = clean_title or "Miscellaneous"

    return best_cat, custom_label, round(float(best_score), 4), ensemble_scores
