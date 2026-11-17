from __future__ import annotations

import re

_STATIC_TRAP_RULES = [
    (
        r"\b(automatically renew|perpetual|evergreen|automatic extension)\b",
        "Automatic Renewal / Evergreen Clause",
        "MEDIUM",
        "The agreement renews automatically. You must track the cancellation window carefully to avoid unwanted rollover.",
    ),
    (
        r"\b(waive(?:s)? (?:any )?right to (?:a )?jury trial|class action waiver|no jury trial)\b",
        "Waiver of Standard Court / Collective Remedies",
        "MEDIUM",
        "Restricts standard civil court or collective dispute remedies (often copied from foreign templates).",
    ),
    (
        r"\b(liquidated damages|forfeited as liquidated damages|penalty amount)\b",
        "Pre-Agreed Financial Penalties (Liquidated Damages)",
        "MEDIUM",
        "Predetermined penalty amount will be assessed immediately upon breach, even if actual damages are significantly lower.",
    ),
    (
        r"\b(shall not be less than\s+(?:one|two|three|five|seven|ten|\d+)\s+years?|imprisonment for life|punished with death)\b",
        "Mandatory Minimum or Severe Criminal Penalty",
        "HIGH",
        "This statutory provision carries a mandatory minimum jail term, life imprisonment, or capital punishment upon conviction.",
    ),
    (
        r"\b(reasonable restrictions|subject to public order,?\s*morality)\b",
        "Constitutional Limitation / Restriction Clause",
        "MEDIUM",
        "The guaranteed right is not absolute; the State may enact statutory restrictions on the grounds listed in this clause.",
    ),
    (
        r"\bnotwithstanding anything contained in\b",
        "Non-Obstante Override Clause",
        "MEDIUM",
        "This provision overrides conflicting sections or clauses elsewhere in the statute or agreement.",
    ),
    (
        r"\bprovided that\b",
        "Statutory Proviso / Built-in Exception",
        "LOW",
        "Contains a 'Provided that' proviso that carves out an exception or extra condition on the main rule—read it alongside the opening sentence.",
    ),
]


def _check_conditional_traps(text_lower: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []

    if re.search(r"\b(indemnif|hold harmless)\b", text_lower) and not re.search(
        r"\b(liability cap|aggregate liability|capped at|not to exceed|maximum liability)\b",
        text_lower,
    ):
        hits.append(
            {
                "trap": "Uncapped Indemnification",
                "severity": "HIGH",
                "explanation": "This clause obligates defense or payment of damages without an explicit dollar cap, exposing you to unlimited financial liability.",
            }
        )

    if re.search(
        r"\b(sole discretion|reserves the right to (?:modify|amend|alter|change)|without (?:prior )?notice)\b",
        text_lower,
    ) and any(word in text_lower for word in ("modify", "amend", "change")):
        hits.append(
            {
                "trap": "Unilateral Modification",
                "severity": "HIGH",
                "explanation": "One party reserves the right to alter contract terms at will without requiring mutual consent or advance notice.",
            }
        )

    cure_match = re.search(
        r"\b(?:within|prior to)\s+(\d+|three|five|seven)\s+(?:business\s+)?days\b",
        text_lower,
    )
    if cure_match and any(word in text_lower for word in ("cure", "default", "notice")):
        hits.append(
            {
                "trap": "Abnormally Short Notice / Cure Window",
                "severity": "MEDIUM",
                "explanation": f"Notice or cure window is restricted to {cure_match.group(0)}, which offers very little time to remedy a disputed breach.",
            }
        )

    if re.search(
        r"\b(non-compete|non-competition|restrictive covenant)\b", text_lower
    ) and (
        re.search(r"\b(two|three|five|2|3|5)\s+years\b", text_lower)
        or "worldwide" in text_lower
    ):
        hits.append(
            {
                "trap": "Extensive Non-Compete Scope",
                "severity": "HIGH",
                "explanation": "The non-compete restricts your post-contract work over an expansive duration or geographic area.",
            }
        )

    if re.search(r"\b(confidentiality|non-disclosure)\b", text_lower) and re.search(
        r"\b(in perpetuity|indefinitely|without limitation of time|survive forever)\b",
        text_lower,
    ):
        hits.append(
            {
                "trap": "Perpetual Confidentiality Burden",
                "severity": "LOW",
                "explanation": "Secrecy obligations continue forever rather than expiring after a typical 2 to 5 year period.",
            }
        )

    return hits


def detect_traps_and_nuances(text: str) -> list[dict[str, str]]:
    """Detect one-sided terms and subtle traps in a clause."""
    if not text:
        return []
    text_lower = text.lower()
    traps = _check_conditional_traps(text_lower)
    for pattern, name, severity, explanation in _STATIC_TRAP_RULES:
        if re.search(pattern, text_lower):
            traps.append(
                {"trap": name, "severity": severity, "explanation": explanation}
            )
    return traps
