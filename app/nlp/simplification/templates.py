from __future__ import annotations

import re

from app.nlp.simplification.rewriter import (
    lexical_simplify,
    split_into_plain_sentences,
    verify_preservation,
)


def _category_intro(category: str, party_str: str) -> str:
    cat_upper = category.upper()
    intros = {
        "INDEMNITY": f"This indemnification provision defines how legal liabilities and defense costs are allocated. Specifically, {party_str} promises to reimburse and defend the other party against legal claims, damages, and attorney fees arising from contract breaches or operational activities.",
        "CONFIDENTIALITY": f"This confidentiality covenant protects proprietary business information from disclosure. {party_str} is legally bound to keep proprietary disclosures secret and use them exclusively for authorized contract purposes.",
        "TERMINATION": "This clause establishes the formal exit procedures for ending this contract. It specifies the conditions required to cancel the agreement, required advance notice, and whether a cure period is granted to fix contract defaults.",
        "GOVERNING_LAW": "This choice of law clause designates which jurisdiction's courts and statutory laws govern any legal dispute. The parties agree to submit exclusively to these courts, avoiding cross-jurisdictional conflicts.",
        "NON_COMPETE": f"This restrictive covenant limits post-employment or post-business competitive activities for {party_str}. It defines the restricted industry scope, duration, and geographic boundaries to protect trade secrets.",
        "PAYMENT": "This financial clause sets the binding monetary terms. It details the payment schedule, invoicing procedures, acceptable payment methods, and any interest penalties for late payments.",
        "LIABILITY": "This limitation of liability clause restricts monetary damages if a legal breach occurs. It typically excludes consequential or indirect damages and caps total liability to protect against excessive lawsuits.",
        "FORCE_MAJEURE": "This force majeure clause excuses performance failures caused by unforeseeable emergencies beyond human control, such as natural disasters, war, strikes, or governmental restrictions.",
        "SEVERABILITY": "This severability provision ensures contract continuity. If a judge or arbitrator strikes down any single clause as illegal or unenforceable, all remaining clauses continue in full legal force.",
    }
    return intros.get(
        cat_upper,
        f"This {category or 'contractual'} clause establishes binding terms and requirements that directly apply to {party_str}.",
    )


def simplify_detailed(
    original_text: str, category: str = "", affected_party: str = ""
) -> str:
    """Produce a contextual explanation filled with extracted timelines and monetary figures."""
    if not original_text or not original_text.strip():
        return ""

    party_str = (
        affected_party
        if affected_party and affected_party != "Unknown"
        else "The responsible party"
    )
    intro = _category_intro(category, party_str)
    lex_text = lexical_simplify(original_text)

    days_match = re.findall(
        r"\b(\d+|thirty|sixty|ninety|ten|fifteen)\s+(?:business\s+)?days\b",
        original_text,
        re.IGNORECASE,
    )
    amounts_match = re.findall(r"[\$₹€£]\s*[\d,]+(?:\.\d{2})?", original_text)

    details: list[str] = []
    if days_match:
        unique_days = list(dict.fromkeys(days_match))
        details.append(
            f"Specified timelines include notice or compliance windows of {', '.join(unique_days)} days."
        )
    if amounts_match:
        unique_amounts = list(dict.fromkeys(amounts_match))
        details.append(
            f"Financial commitments or caps noted in the text include {', '.join(unique_amounts)}."
        )

    core_content = " ".join(split_into_plain_sentences(lex_text)[:3])
    full_detailed = f"{intro}\n\nCore Terms: {core_content}"
    if details:
        full_detailed += " " + " ".join(details)

    if not verify_preservation(original_text, full_detailed):
        return f"{intro}\n\nTerms: {lex_text}"
    return full_detailed


def _extract_covenant_type(text: str) -> str:
    if re.search(
        r"\b(shall not|must not|may not|prohibited|refrain)\b", text, re.IGNORECASE
    ):
        return "Negative Covenant (Strict Prohibition)"
    if re.search(
        r"\b(shall|must|agrees to|obligated|required to)\b", text, re.IGNORECASE
    ):
        return "Affirmative Covenant (Mandatory Performance)"
    return "Declaratory Covenant / Procedural Condition"


def simplify_professional(
    original_text: str, category: str = "", affected_party: str = ""
) -> str:
    """Produce a structured breakdown of obligor, duty, conditions, exceptions, and remedies."""
    if not original_text or not original_text.strip():
        return ""

    party_str = (
        affected_party
        if affected_party and affected_party != "Unknown"
        else "Contracting Party"
    )
    core_type = _extract_covenant_type(original_text)

    cond_match = re.search(
        r"\b(?:in the event(?: that)?|upon|if|subject to|provided that)\s+([^,.;]{10,80})",
        original_text,
        re.IGNORECASE,
    )
    trigger = (
        cond_match.group(0).strip()
        if cond_match
        else "Immediate upon execution / standard operation"
    )

    exc_match = re.search(
        r"\b(?:except|unless|other than|excluding|provided however that)\s+([^,.;]{10,80})",
        original_text,
        re.IGNORECASE,
    )
    exceptions = (
        exc_match.group(0).strip()
        if exc_match
        else "None explicitly stated in this clause"
    )

    time_match = re.search(
        r"\b(?:within|prior to|after|on or before)\s+([^,.;]{5,50})",
        original_text,
        re.IGNORECASE,
    )
    timeline = (
        time_match.group(0).strip()
        if time_match
        else "Standard business practice / Not specified"
    )

    rem_match = re.search(
        r"\b(injunction|injunctive relief|liquidated damages|terminate|damages|attorney(?:s')? fees)\b",
        original_text,
        re.IGNORECASE,
    )
    remedy = (
        f"Legal or equitable relief ({rem_match.group(0)})"
        if rem_match
        else "Breach of contract damages and statutory remedies"
    )

    short_duty = lexical_simplify(original_text).split(".")[0].strip()
    if len(short_duty) > 140:
        short_duty = short_duty[:137] + "..."

    return (
        f"• **Obligor / Bound Party**: {party_str}\n"
        f"• **Covenant Type**: {core_type}\n"
        f"• **Core Duty**: {short_duty}\n"
        f"• **Conditions & Triggers**: {trigger}\n"
        f"• **Exceptions & Carve-Outs**: {exceptions}\n"
        f"• **Timeline / Cure Period**: {timeline}\n"
        f"• **Remedies & Liabilities**: {remedy}"
    )
