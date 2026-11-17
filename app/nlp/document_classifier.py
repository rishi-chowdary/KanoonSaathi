import re
from pathlib import Path

import numpy as np
import yaml

from app.nlp.registry import get_sentence_transformer

# Document type regexes for fast and accurate heading detection
DOCUMENT_TYPE_PATTERNS = [
    (
        r"\b(?:non[\s-]disclosure|confidential(?:ity)?\s+agreement|mutual\s+nda)\b",
        "Non-Disclosure Agreement (NDA)",
    ),
    (
        r"\b(?:residential\s+lease|rental\s+agreement|lease\s+agreement|tenancy\s+agreement)\b",
        "Residential Lease Agreement",
    ),
    (
        r"\b(?:executive\s+employment|employment\s+agreement|employment\s+contract)\b",
        "Executive Employment Agreement",
    ),
    (
        r"\b(?:master\s+services|vendor\s+agreement|services\s+agreement|statement\s+of\s+work)\b",
        "Master Services Agreement",
    ),
    (
        r"\b(?:promissory\s+note|loan\s+agreement|note\s+payable)\b",
        "Promissory Note",
    ),
    (
        r"\b(?:quitclaim\s+deed|warranty\s+deed|grant\s+deed|deed\s+of\s+trust)\b",
        "Property Deed",
    ),
]

_doc_prototypes: dict[str, np.ndarray] | None = None


def _load_doc_prototypes() -> dict[str, np.ndarray]:
    global _doc_prototypes
    if _doc_prototypes is not None:
        return _doc_prototypes

    proto_path = Path("data/clause_prototypes.yaml")
    if not proto_path.exists():
        return {}

    with open(proto_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    doc_types = data.get("document_types", {})
    model = get_sentence_transformer()

    embedded: dict[str, np.ndarray] = {}
    for doc_type, descriptions in doc_types.items():
        if descriptions:
            vecs = model.encode(descriptions, convert_to_numpy=True)
            if vecs.ndim == 1:
                vecs = vecs.reshape(1, -1)
            mean_vec = np.mean(vecs, axis=0)
            norm = np.linalg.norm(mean_vec)
            if norm > 0:
                mean_vec = mean_vec / norm
            embedded[doc_type] = mean_vec

    _doc_prototypes = embedded
    return _doc_prototypes


def classify_document_type(full_text: str, filename: str = "") -> tuple[str, float]:
    """Classify the legal document type using heading pattern matching and SBERT prototypes.

    Returns:
        tuple of (document_type_name, confidence_score)
    """
    if not full_text:
        return "General Contract", 0.0

    header_sample = full_text[:1200]
    for pattern, doc_type in DOCUMENT_TYPE_PATTERNS:
        if re.search(pattern, header_sample, re.IGNORECASE):
            return doc_type, 0.95

    # Also check filename if informative
    for pattern, doc_type in DOCUMENT_TYPE_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return doc_type, 0.85

    # 2. SBERT Zero-Shot Prototype Cosine Similarity Fallback
    prototypes = _load_doc_prototypes()
    if not prototypes:
        return "General Contract", 0.50

    model = get_sentence_transformer()
    doc_embedding = model.encode([header_sample[:500]], convert_to_numpy=True)[0]
    doc_norm = np.linalg.norm(doc_embedding)
    if doc_norm > 0:
        doc_embedding = doc_embedding / doc_norm

    best_type = "General Contract"
    best_score = -1.0

    for doc_type, proto_vec in prototypes.items():
        similarity = float(np.dot(doc_embedding, proto_vec))
        if similarity > best_score:
            best_score = similarity
            best_type = doc_type

    confidence = max(0.1, min(1.0, float(best_score)))
    return best_type, confidence
