"""Rule-based clause simplification in three modes: simple, detailed, and professional."""

from __future__ import annotations

from typing import Any

from app.nlp.readability import calculate_readability
from app.nlp.simplification.glossary import (
    extract_clause_glossary,
    get_glossary,
    get_sorted_glossary_terms,
)
from app.nlp.simplification.rewriter import (
    lexical_simplify,
    simplify_simple_english,
    split_into_plain_sentences,
    verify_preservation,
)
from app.nlp.simplification.templates import simplify_detailed, simplify_professional
from app.nlp.simplification.traps import detect_traps_and_nuances


def simplify_clause(
    original_text: str,
    category: str = "",
    affected_party: str = "",
) -> dict[str, Any]:
    """Simplify a clause into simple, detailed, and professional modes with readability scores."""
    if not original_text or not original_text.strip():
        empty_readability = calculate_readability("")
        return {
            "simple_english": "",
            "detailed": "",
            "professional": "",
            "readability_original": empty_readability,
            "readability_simple": empty_readability,
            "readability_detailed": empty_readability,
            "glossary_terms": [],
            "traps_and_nuances": [],
            "preservation_verified": True,
        }

    simple_eng = simplify_simple_english(original_text, category, affected_party)
    detailed = simplify_detailed(original_text, category, affected_party)
    professional = simplify_professional(original_text, category, affected_party)

    is_verified = verify_preservation(
        original_text, simple_eng
    ) and verify_preservation(original_text, detailed)

    return {
        "simple_english": simple_eng,
        "detailed": detailed,
        "professional": professional,
        "readability_original": calculate_readability(original_text),
        "readability_simple": calculate_readability(simple_eng),
        "readability_detailed": calculate_readability(detailed),
        "glossary_terms": extract_clause_glossary(original_text),
        "traps_and_nuances": detect_traps_and_nuances(original_text),
        "preservation_verified": is_verified,
    }


__all__ = [
    "detect_traps_and_nuances",
    "extract_clause_glossary",
    "get_glossary",
    "get_sorted_glossary_terms",
    "lexical_simplify",
    "simplify_clause",
    "simplify_detailed",
    "simplify_professional",
    "simplify_simple_english",
    "split_into_plain_sentences",
    "verify_preservation",
]
