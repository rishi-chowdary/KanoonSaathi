"""Offline Indian statute detection and BNS <-> IPC / Constitution lookup."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

STATUTES_PATH = Path("data/indian_statutes.yaml")


@lru_cache(maxsize=1)
def load_indian_statutes() -> dict[str, list[dict[str, Any]]]:
    """Load BNS/IPC sections, Constitutional articles, and civil laws from local YAML."""
    if not STATUTES_PATH.exists():
        return {
            "criminal_sections": [],
            "constitutional_articles": [],
            "civil_and_special_laws": [],
        }
    with open(STATUTES_PATH, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return {
        "criminal_sections": raw.get("criminal_sections", []),
        "constitutional_articles": raw.get("constitutional_articles", []),
        "civil_and_special_laws": raw.get("civil_and_special_laws", []),
    }


def _build_indexes() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    data = load_indian_statutes()
    by_bns: dict[str, dict[str, Any]] = {}
    by_ipc: dict[str, dict[str, Any]] = {}
    by_art: dict[str, dict[str, Any]] = {}

    for entry in data["criminal_sections"]:
        bns_num = str(entry.get("bns_section", "")).strip().upper()
        if bns_num:
            by_bns[bns_num] = entry
        ipc_raw = str(entry.get("ipc_section", ""))
        for token in re.findall(r"\b(\d{1,3}[A-Z]?)\b", ipc_raw.upper()):
            by_ipc[token] = entry

    for entry in data["constitutional_articles"]:
        art_num = str(entry.get("article", "")).strip().upper()
        if art_num:
            by_art[art_num] = entry

    return by_bns, by_ipc, by_art


_BNS_REF_RE = re.compile(
    r"(?:"
    r"\b(?:section|sec\.?|s\.|u/s)\s*(\d{1,3}[A-Z]?)(?:\(\d+\))?\s*(?:of\s+(?:the\s+)?)?(?:bns|bharatiya\s+nyaya\s+sanhita)\b"
    r"|\b(?:bns|bharatiya\s+nyaya\s+sanhita)\s*(?:,?\s*2023)?\s*(?:section|sec\.?|s\.?)?\s*(\d{1,3}[A-Z]?)(?:\(\d+\))?\b"
    r")",
    re.IGNORECASE,
)

_IPC_REF_RE = re.compile(
    r"(?:"
    r"\b(?:section|sec\.?|s\.|u/s)\s*(\d{1,3}[A-Z]?)(?:\(\d+\))?\s*(?:of\s+(?:the\s+)?)?(?:ipc|indian\s+penal\s+code)\b"
    r"|\b(?:ipc|indian\s+penal\s+code)\s*(?:,?\s*1860)?\s*(?:section|sec\.?|s\.?)?\s*(\d{1,3}[A-Z]?)(?:\(\d+\))?\b"
    r")",
    re.IGNORECASE,
)

_ART_REF_RE = re.compile(
    r"\b(?:article|art\.?)\s*(\d{1,3}[A-Z]?)(?:\(\d+\))?(?:\([a-z]\))?\b",
    re.IGNORECASE,
)

_BARE_SECTION_RE = re.compile(
    r"\b(?:section|sec\.?)\s*(\d{1,3}[A-Z]?)(?:\(\d+\))?\b",
    re.IGNORECASE,
)


def _format_criminal_ref(entry: dict[str, Any], matched_via: str) -> dict[str, Any]:
    return {
        "statute_type": matched_via,
        "bns_section": entry["bns_section"],
        "ipc_section": entry["ipc_section"],
        "title": entry["title"],
        "punishment": entry.get("punishment", ""),
        "cognizable": entry.get("cognizable", ""),
        "bailable": entry.get("bailable", ""),
        "plain_english": entry.get("plain_english", ""),
        "label": f"BNS {entry['bns_section']} <-> IPC {entry['ipc_section']}: {entry['title']}",
    }


def _format_constitutional_ref(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "statute_type": "Constitution",
        "article": entry["article"],
        "part": entry.get("part", ""),
        "title": entry["title"],
        "scope": entry.get("scope", ""),
        "key_restrictions": entry.get("key_restrictions", ""),
        "plain_english": entry.get("plain_english", ""),
        "label": f"Article {entry['article']} ({entry.get('part', 'Constitution')}): {entry['title']}",
    }


def detect_statute_references(
    text: str, document_type: str = ""
) -> list[dict[str, Any]]:
    """Detect BNS, IPC, and Constitutional references in text and attach offline mappings."""
    if not text:
        return []

    by_bns, by_ipc, by_art = _build_indexes()
    seen_ids: set[str] = set()
    matches: list[dict[str, Any]] = []

    def add_criminal(entry: dict[str, Any], via: str) -> None:
        if entry["id"] not in seen_ids:
            seen_ids.add(entry["id"])
            matches.append(_format_criminal_ref(entry, via))

    for m in _BNS_REF_RE.finditer(text):
        sec = (m.group(1) or m.group(2) or "").upper()
        if sec in by_bns:
            add_criminal(by_bns[sec], "BNS")

    for m in _IPC_REF_RE.finditer(text):
        sec = (m.group(1) or m.group(2) or "").upper()
        if sec in by_ipc:
            add_criminal(by_ipc[sec], "IPC")

    for m in _ART_REF_RE.finditer(text):
        art = m.group(1).upper()
        if art in by_art and by_art[art]["id"] not in seen_ids:
            seen_ids.add(by_art[art]["id"])
            matches.append(_format_constitutional_ref(by_art[art]))

    # When text itself comes from a BNS or IPC excerpt without repeating "BNS"/"IPC" in every section
    doc_lower = f"{document_type} {text[:300]}".lower()
    is_bns_context = "bharatiya nyaya sanhita" in doc_lower or "sanhita" in doc_lower
    is_ipc_context = "indian penal code" in doc_lower or "penal code" in doc_lower
    if is_bns_context or is_ipc_context:
        for m in _BARE_SECTION_RE.finditer(text):
            sec = m.group(1).upper()
            if is_bns_context and sec in by_bns:
                add_criminal(by_bns[sec], "BNS")
            elif is_ipc_context and sec in by_ipc:
                add_criminal(by_ipc[sec], "IPC")

    return matches


def search_indian_statutes(
    query: str = "", statute_type: str = "all"
) -> list[dict[str, Any]]:
    """Search offline BNS, IPC, and Constitutional entries by section, article, or keyword."""
    data = load_indian_statutes()
    q = query.strip().lower()
    stype = (statute_type or "all").strip().lower()
    results: list[dict[str, Any]] = []

    if stype in ("all", "bns", "ipc", "criminal"):
        for entry in data["criminal_sections"]:
            haystack = " ".join(
                [
                    f"bns {entry['bns_section']}",
                    f"section {entry['bns_section']}",
                    f"ipc {entry['ipc_section']}",
                    entry["title"],
                    entry.get("chapter", ""),
                    entry.get("plain_english", ""),
                    entry.get("punishment", ""),
                ]
            ).lower()
            if not q or q in haystack:
                results.append(
                    {
                        "id": entry["id"],
                        "kind": "criminal",
                        "bns_section": entry["bns_section"],
                        "ipc_section": entry["ipc_section"],
                        "title": entry["title"],
                        "chapter": entry.get("chapter", ""),
                        "cognizable": entry.get("cognizable", ""),
                        "bailable": entry.get("bailable", ""),
                        "punishment": entry.get("punishment", ""),
                        "plain_english": entry.get("plain_english", ""),
                        "excerpt": entry.get("excerpt", ""),
                    }
                )

    if stype in ("all", "constitution", "constitutional", "article"):
        for entry in data["constitutional_articles"]:
            haystack = " ".join(
                [
                    f"article {entry['article']}",
                    f"art {entry['article']}",
                    entry["title"],
                    entry.get("part", ""),
                    entry.get("plain_english", ""),
                    entry.get("scope", ""),
                    entry.get("key_restrictions", ""),
                ]
            ).lower()
            if not q or q in haystack:
                results.append(
                    {
                        "id": entry["id"],
                        "kind": "constitution",
                        "article": entry["article"],
                        "part": entry.get("part", ""),
                        "title": entry["title"],
                        "scope": entry.get("scope", ""),
                        "key_restrictions": entry.get("key_restrictions", ""),
                        "plain_english": entry.get("plain_english", ""),
                        "excerpt": entry.get("excerpt", ""),
                    }
                )

    return results
