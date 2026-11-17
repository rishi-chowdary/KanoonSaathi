"""Offline citizen legal-issue matcher for Indian laws (BNS, IPC, Constitution, civil remedies)."""

from __future__ import annotations

import re
from typing import Any

import numpy as np

from app.nlp.indian_law import load_indian_statutes
from app.nlp.registry import get_sentence_transformer
from app.nlp.risk_engine import soften_legal_claims

_DISCLAIMER = (
    "Informational reference only — not legal advice. Only police, courts, or a "
    "qualified advocate can decide which sections apply to your exact facts. "
    "Free legal aid is available across India through NALSA (Helpline 15100)."
)

# Everyday citizen phrasing cues mapped to statute IDs for keyword recall alongside SBERT
_SCENARIO_CUES: dict[str, list[str]] = {
    "BNS_61": ["conspiracy", "planned together", "plotted", "gang planned"],
    "BNS_64": ["rape", "sexual assault"],
    "BNS_69": ["false promise of marriage", "marriage deceit", "lied about marriage"],
    "BNS_74": ["molested", "groped", "outrage modesty", "inappropriate touching"],
    "BNS_78": [
        "stalking",
        "stalking me",
        "following me",
        "constantly messaging",
        "harassing online",
    ],
    "BNS_80": ["dowry death", "burned for dowry", "unnatural death marriage"],
    "BNS_85": [
        "dowry",
        "husband beating",
        "in-laws harassing",
        "cruelty by husband",
        "domestic cruelty",
    ],
    "BNS_103": ["murder", "killed someone", "mob lynching", "homicide"],
    "BNS_105": ["culpable homicide", "caused death", "manslaughter"],
    "BNS_106": [
        "hit and run",
        "rash driving death",
        "negligent driving",
        "fatal crash",
    ],
    "BNS_111": ["organised crime", "gang extortion", "syndicate", "land grabbing"],
    "BNS_115": ["beat me", "slapped", "punched", "assaulted", "hit me", "caused hurt"],
    "BNS_117": [
        "fracture",
        "broken bone",
        "grievous hurt",
        "severe injury",
        "hospitalized",
    ],
    "BNS_126": ["blocked my way", "stopped me from leaving", "wrongful restraint"],
    "BNS_137": ["kidnapped", "abducted", "missing child", "taken away minor"],
    "BNS_189": ["mob", "unlawful assembly", "group attacked"],
    "BNS_303": [
        "stolen",
        "stole",
        "theft",
        "bike stolen",
        "car stolen",
        "pickpocket",
        "burgled",
    ],
    "BNS_304": [
        "snatched",
        "phone snatched",
        "chain snatched",
        "grabbed my bag",
        "bike snatching",
    ],
    "BNS_308": ["extortion", "blackmail", "demanding money", "pay or else"],
    "BNS_309": ["robbery", "robbed", "looted", "mugged", "knife point", "gun point"],
    "BNS_316": [
        "breach of trust",
        "entrusted",
        "refused to return",
        "kept my money",
        "misappropriated",
        "took my gold",
        "took my property",
    ],
    "BNS_318": [
        "cheated",
        "cheating",
        "fraud",
        "scam",
        "fake job",
        "tricked me",
        "took money and disappeared",
        "deceived",
        "420",
        "ponzi",
    ],
    "BNS_329": [
        "trespass",
        "entered my house",
        "entered my land",
        "encroachment",
        "illegally occupying",
        "refusing to leave property",
    ],
    "BNS_336": ["forged", "forgery", "fake signature", "fake document", "counterfeit"],
    "BNS_351": [
        "threatened",
        "threatening",
        "death threat",
        "threat to kill",
        "intimidation",
        "threatening my family",
    ],
    "BNS_356": [
        "defamation",
        "false rumors",
        "ruin my reputation",
        "posted lies",
        "slander",
        "libel",
        "false accusation online",
    ],
    "ART_14": ["unequal treatment", "arbitrary government", "equality before law"],
    "ART_15": [
        "discrimination",
        "caste discrimination",
        "religion discrimination",
        "denied entry",
    ],
    "ART_16": ["government job discrimination", "public employment"],
    "ART_17": ["untouchability"],
    "ART_19": [
        "freedom of speech",
        "peaceful protest",
        "right to assemble",
        "right to business",
    ],
    "ART_20": [
        "forced to confess",
        "double jeopardy",
        "punished twice",
        "self incrimination",
    ],
    "ART_21": [
        "life and liberty",
        "illegal detention",
        "privacy violated",
        "right to life",
    ],
    "ART_21A": ["child education", "school admission denied", "free education"],
    "ART_22": [
        "arrested by police",
        "police arrested",
        "without telling reason",
        "magistrate 24 hours",
        "not produced before magistrate",
        "denied lawyer",
        "police custody",
    ],
    "ART_25": ["freedom of religion", "religious practice"],
    "ART_32": [
        "supreme court writ",
        "habeas corpus",
        "fundamental right violated",
        "mandamus",
    ],
    "ART_226": ["high court writ", "writ petition", "habeas corpus", "quash order"],
    "ART_300A": [
        "government took land",
        "property demolished without notice",
        "land acquisition",
    ],
}

_CANDIDATE_CACHE: tuple[list[dict[str, Any]], np.ndarray] | None = None


def _criminal_next_steps(entry: dict[str, Any]) -> list[str]:
    steps = [
        "Write down exact dates, times, locations, names, and preserve evidence (messages, call logs, receipts, photos, or CCTV).",
    ]
    cog = str(entry.get("cognizable", "")).lower()
    if "non-cognizable" in cog and "cognizable" not in cog.replace(
        "non-cognizable", ""
    ):
        steps.append(
            "For non-cognizable offences, file a written Non-Cognizable Report (NCR) at the local police station or approach a Magistrate with an advocate."
        )
    else:
        steps.append(
            "Visit the local police station (or dial 112 in an emergency) to submit a signed written complaint for registering an FIR under BNSS Section 173."
        )
    steps.append(
        "Consult a criminal lawyer or contact NALSA free legal aid (Helpline 15100) to confirm the exact sections."
    )
    return steps


def _build_candidates() -> list[dict[str, Any]]:
    data = load_indian_statutes()
    candidates: list[dict[str, Any]] = []

    for entry in data["criminal_sections"]:
        cues = _SCENARIO_CUES.get(entry["id"], [])
        embed_text = (
            f"BNS Section {entry['bns_section']} IPC {entry['ipc_section']} "
            f"{entry['title']}. {entry['plain_english']} {' '.join(cues)}"
        )
        cog = entry.get("cognizable", "")
        bail = entry.get("bailable", "")
        candidates.append(
            {
                "id": entry["id"],
                "category": "Criminal Law (BNS / IPC)",
                "citation": f"BNS Section {entry['bns_section']} (formerly IPC {entry['ipc_section']})",
                "title": entry["title"],
                "plain_english": soften_legal_claims(entry["plain_english"]),
                "details": f"Punishment: {entry.get('punishment', '')} Status: {cog}; {bail}.",
                "where_to_file": "Local Police Station (FIR / NCR under BNSS) or Judicial Magistrate Court",
                "next_steps": _criminal_next_steps(entry),
                "excerpt": entry.get("excerpt", ""),
                "studio_category": "BNS_SECTION",
                "keywords": cues
                + [entry["title"].lower(), f"bns {entry['bns_section']}".lower()],
                "embed_text": embed_text,
            }
        )

    for entry in data["constitutional_articles"]:
        cues = _SCENARIO_CUES.get(entry["id"], [])
        embed_text = (
            f"Constitution of India Article {entry['article']} {entry['title']}. "
            f"{entry['plain_english']} {' '.join(cues)}"
        )
        candidates.append(
            {
                "id": entry["id"],
                "category": "Constitutional Right",
                "citation": f"Constitution of India — Article {entry['article']}",
                "title": entry["title"],
                "plain_english": soften_legal_claims(entry["plain_english"]),
                "details": f"Scope: {entry.get('scope', '')}. Restrictions: {entry.get('key_restrictions', '')}",
                "where_to_file": "State High Court (Writ Petition under Article 226) or Supreme Court (Article 32)",
                "next_steps": [
                    "Keep copies of any official orders, arrest memos, notices, or written communications showing the violation.",
                    "Consult an advocate practising in the High Court or contact Legal Services Authority (NALSA 15100) regarding a writ petition.",
                ],
                "excerpt": entry.get("excerpt", ""),
                "studio_category": "CONSTITUTIONAL_CLAUSE",
                "keywords": cues
                + [entry["title"].lower(), f"article {entry['article']}".lower()],
                "embed_text": embed_text,
            }
        )

    for entry in data["civil_and_special_laws"]:
        cues = entry.get("keywords", [])
        embed_text = (
            f"{entry['act']} {entry['section']} {entry['title']}. "
            f"{entry['plain_english']} {' '.join(cues)}"
        )
        candidates.append(
            {
                "id": entry["id"],
                "category": "Civil / Special Law",
                "citation": f"{entry['act']} — {entry['section']}",
                "title": entry["title"],
                "plain_english": soften_legal_claims(entry["plain_english"]),
                "details": f"Typical remedy: {entry.get('remedy', '')}",
                "where_to_file": entry.get(
                    "forum", "Competent Civil Court / Statutory Authority"
                ),
                "next_steps": entry.get("next_steps", []),
                "excerpt": "",
                "studio_category": "INDIAN_STATUTE",
                "keywords": [k.lower() for k in cues] + [entry["title"].lower()],
                "embed_text": embed_text,
            }
        )

    return candidates


def _get_embedded_candidates() -> tuple[list[dict[str, Any]], np.ndarray]:
    global _CANDIDATE_CACHE
    if _CANDIDATE_CACHE is not None:
        return _CANDIDATE_CACHE

    candidates = _build_candidates()
    model = get_sentence_transformer()
    texts = [c["embed_text"] for c in candidates]
    vecs = model.encode(texts, convert_to_numpy=True)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vecs = vecs / norms
    _CANDIDATE_CACHE = (candidates, vecs)
    return _CANDIDATE_CACHE


def _keyword_bonus(query_lower: str, keywords: list[str]) -> float:
    hits = 0
    for kw in keywords:
        if not kw or len(kw) < 3:
            continue
        if re.search(r"\b" + re.escape(kw) + r"\b", query_lower):
            hits += 2 if " " in kw else 1
    return min(0.35, hits * 0.12)


def match_legal_issue(user_issue: str, top_k: int = 4) -> dict[str, Any]:
    """Match an everyday citizen issue description to possible Indian legal sections and next steps."""
    clean_issue = (user_issue or "").strip()
    if len(clean_issue) < 6:
        return {
            "matched": False,
            "summary": "Please describe your issue in a sentence or two (for example: cheque bounce, online fraud, unpaid salary, landlord keeping security deposit, or police arrest).",
            "disclaimer": _DISCLAIMER,
            "suggestions": [],
        }

    candidates, vecs = _get_embedded_candidates()
    model = get_sentence_transformer()
    q_vec = model.encode([clean_issue], convert_to_numpy=True)[0]
    q_norm = np.linalg.norm(q_vec)
    if q_norm > 0:
        q_vec = q_vec / q_norm

    sims = np.dot(vecs, q_vec)
    query_lower = clean_issue.lower()

    scored: list[tuple[float, float, dict[str, Any]]] = []
    for idx, cand in enumerate(candidates):
        sem_score = float(sims[idx])
        kw_bonus = _keyword_bonus(query_lower, cand["keywords"])
        combined = sem_score + kw_bonus
        scored.append((combined, sem_score, cand))

    scored.sort(key=lambda x: x[0], reverse=True)
    best_combined = scored[0][0] if scored else 0.0

    # Refuse honestly when the input is unrelated to legal issues
    if best_combined < 0.34:
        return {
            "matched": False,
            "summary": (
                "No matching Indian legal sections were found for this description. "
                "Try describing the specific problem—such as fraud or scam, cheque bounce, "
                "unpaid salary, landlord deposit dispute, theft, threats, defamation, or wrongful arrest."
            ),
            "disclaimer": _DISCLAIMER,
            "suggestions": [],
        }

    cutoff = max(0.34, best_combined - 0.18)
    suggestions: list[dict[str, Any]] = []
    for combined, sem_score, cand in scored[:top_k]:
        if combined < cutoff:
            continue
        relevance = "Strong match" if combined >= 0.52 else "Possible match"
        suggestions.append(
            {
                "id": cand["id"],
                "citation": cand["citation"],
                "title": cand["title"],
                "category": cand["category"],
                "relevance": relevance,
                "confidence": round(min(0.99, combined), 2),
                "plainEnglish": cand["plain_english"],
                "details": cand["details"],
                "whereToFile": cand["where_to_file"],
                "nextSteps": cand["next_steps"],
                "excerpt": cand["excerpt"],
                "studioCategory": cand["studio_category"],
            }
        )

    citations_list = ", ".join(s["citation"] for s in suggestions[:3])
    summary = (
        f"Based on your description, these Indian legal provisions may be relevant to review "
        f"or discuss with an advocate or local authority: {citations_list}."
    )

    return {
        "matched": True,
        "summary": soften_legal_claims(summary),
        "disclaimer": _DISCLAIMER,
        "suggestions": suggestions,
    }
