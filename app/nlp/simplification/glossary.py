from __future__ import annotations

import os
import re
from functools import lru_cache

import yaml

_GLOSSARY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "data",
    "glossary.yaml",
)


@lru_cache(maxsize=1)
def get_glossary() -> dict[str, dict[str, str]]:
    if not os.path.exists(_GLOSSARY_PATH):
        return {}
    with open(_GLOSSARY_PATH, encoding="utf-8") as f:
        raw_glossary = yaml.safe_load(f) or {}
    return raw_glossary.get("terms", {})


@lru_cache(maxsize=1)
def get_sorted_glossary_terms() -> list[tuple[str, str, str, str]]:
    glossary = get_glossary()
    entries = [
        (
            term,
            meta.get("plain_replacement", term),
            meta.get("definition", ""),
            meta.get("category", "General"),
        )
        for term, meta in glossary.items()
    ]
    entries.sort(key=lambda entry: len(entry[0]), reverse=True)
    return entries


def extract_clause_glossary(text: str) -> list[dict[str, str]]:
    """Return glossary terms found in a clause with plain replacements and definitions."""
    if not text:
        return []
    found: list[dict[str, str]] = []
    seen: set[str] = set()

    for term, replacement, definition, category in get_sorted_glossary_terms():
        pattern = rf"\b{re.escape(term)}\b"
        if re.search(pattern, text, re.IGNORECASE) and term.lower() not in seen:
            seen.add(term.lower())
            found.append(
                {
                    "term": term,
                    "plain_replacement": replacement,
                    "definition": definition,
                    "category": category,
                }
            )
    return found
