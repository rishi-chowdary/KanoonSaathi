"""LexiLegal AI — Grounded Contract Risk Detection Engine.

Rule-based + SBERT prototype semantic similarity risk detector:
- Identifies contractual, financial, liability, employment, privacy, and legal risks
- Extracts exact, verified evidence quotes anchored to source page
- Strictly complies with Rule 7: zero legal conclusions ("illegal", "void", "unenforceable")
- Adds jurisdiction caveat when governing law is unknown or non-specific
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Any

import numpy as np
import yaml

from app.nlp.evidence import extract_evidence_quote
from app.nlp.registry import get_sbert

_RULES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "risk_rules.yaml",
)

# Rule 7: Forbidden legal conclusions and safe non-definitive replacements
RULE7_FORBIDDEN_REPLACEMENTS = [
    (re.compile(r"\bnull\s+and\s+void\b", re.IGNORECASE), "invalid"),
    (re.compile(r"\billegal\b", re.IGNORECASE), "potentially unfavorable"),
    (re.compile(r"\billegality\b", re.IGNORECASE), "potential unenforceability"),
    (
        re.compile(r"\bunlawful\b", re.IGNORECASE),
        "non-standard under general commercial practice",
    ),
    (re.compile(r"\bvoid\b", re.IGNORECASE), "questionable under standard practice"),
    (re.compile(r"\bunenforceable\b", re.IGNORECASE), "subject to legal challenge"),
    (
        re.compile(r"\bunenforceability\b", re.IGNORECASE),
        "potential difficulty in enforcement",
    ),
]


def enforce_rule7_language(text: str) -> str:
    """Ensure text strictly avoids definitive legal conclusions per Rule 7."""
    if not text:
        return ""
    out = text
    for pattern, repl in RULE7_FORBIDDEN_REPLACEMENTS:
        out = pattern.sub(repl, out)
    return out


def count_rule7_violations(text: str) -> int:
    """Return count of forbidden legal conclusion words (must be 0 in all outputs)."""
    if not text:
        return 0
    forbidden = re.findall(
        r"\b(illegal|illegality|unlawful|void|unenforceable)\b", text, re.IGNORECASE
    )
    return len(forbidden)


@lru_cache(maxsize=1)
def load_risk_rules() -> list[dict[str, Any]]:
    """Load risk detection rules from data/risk_rules.yaml."""
    if not os.path.exists(_RULES_PATH):
        return []
    with open(_RULES_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("rules", [])


@lru_cache(maxsize=1)
def load_rule_embeddings() -> list[tuple[dict[str, Any], np.ndarray]]:
    """Precompute SBERT embeddings for rule prototypes."""
    rules = load_risk_rules()
    sbert = get_sbert()
    encoded_rules: list[tuple[dict[str, Any], np.ndarray]] = []

    for rule in rules:
        prototypes = rule.get("prototypes", [])
        if prototypes:
            emb = sbert.encode(prototypes, normalize_embeddings=True)
            encoded_rules.append((rule, emb))
        else:
            encoded_rules.append((rule, np.zeros((1, 384))))

    return encoded_rules


def detect_clause_risks(
    clauses: list[Any],
    full_text: str = "",
    governing_law_stated: bool = False,
) -> list[dict[str, Any]]:
    """Scan clauses for contractual, financial, liability, and operational risks.

    Returns deduplicated, prioritized list of risk finding dictionaries.
    """
    if not clauses:
        return []

    sbert = get_sbert()
    rule_embeddings = load_rule_embeddings()

    # Pre-embed clause texts for batch cosine similarity
    clause_texts = [
        f"{getattr(c, 'title', '')}: {getattr(c, 'original_text', '')}" for c in clauses
    ]
    clause_embs = sbert.encode(clause_texts, normalize_embeddings=True)

    detected_risks: list[dict[str, Any]] = []
    seen_rule_ids: set[str] = set()

    for idx, clause in enumerate(clauses):
        c_title = getattr(clause, "title", "Clause")
        c_text = getattr(clause, "original_text", "")
        c_page = getattr(clause, "source_page", 1)
        c_emb = clause_embs[idx]

        for rule, proto_embs in rule_embeddings:
            rule_id = rule["id"]
            if rule_id in seen_rule_ids:
                continue

            pattern_matched = False
            # 1. Regex pattern check
            for pat in rule.get("patterns", []):
                if re.search(pat, c_text, re.IGNORECASE):
                    pattern_matched = True
                    break

            # 2. SBERT semantic similarity check
            sim_score = 0.0
            if proto_embs.shape[0] > 0 and proto_embs.shape[1] == c_emb.shape[0]:
                similarities = np.dot(proto_embs, c_emb)
                sim_score = float(np.max(similarities))

            semantic_matched = sim_score >= 0.65

            if pattern_matched or semantic_matched:
                seen_rule_ids.add(rule_id)

                # Extract exact evidence quote anchored to source page
                quote, verified = extract_evidence_quote(
                    original_text=c_text,
                    category=rule.get("category", ""),
                    title=c_title,
                )

                jurisdiction_caveat = (
                    None
                    if governing_law_stated
                    else "Governing law may affect enforceability in your specific jurisdiction."
                )

                risk_entry = {
                    "rule_id": rule_id,
                    "category": rule["category"],
                    "level": rule["level"],
                    "title": enforce_rule7_language(rule["title"]),
                    "original_clause": c_text,
                    "explanation": enforce_rule7_language(rule["explanation"]),
                    "why_it_matters": enforce_rule7_language(rule["why_it_matters"]),
                    "possible_consequences": enforce_rule7_language(
                        rule["possible_consequences"]
                    ),
                    "suggested_questions": [
                        enforce_rule7_language(q)
                        for q in rule.get("suggested_questions", [])
                    ],
                    "source_page": c_page,
                    "evidence_quote": quote,
                    "quote_verified": verified,
                    "jurisdiction_caveat": jurisdiction_caveat,
                    "provenance": (
                        "RULE_BASED" if pattern_matched else "MODEL_PREDICTION"
                    ),
                    "similarity_score": round(sim_score, 3),
                }

                detected_risks.append(risk_entry)

    # Sort risks by severity: HIGH > MEDIUM > LOW > INFORMATIONAL
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFORMATIONAL": 3}
    detected_risks.sort(key=lambda r: severity_order.get(r["level"], 4))

    return detected_risks
