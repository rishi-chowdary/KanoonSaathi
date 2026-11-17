from __future__ import annotations

import re

from app.nlp.simplification.rewriter import (
    lexical_simplify,
    split_into_plain_sentences,
    verify_preservation,
)


def _category_intro(category: str, party_str: str) -> str:
    cat_upper = category.upper().replace(" ", "_")
    intros = {
        "BNS_SECTION": "This Bharatiya Nyaya Sanhita (BNS, 2023) section defines a criminal offence or statutory punishment under Indian criminal law.",
        "IPC_SECTION": "This Indian Penal Code (IPC, 1860) section defines a criminal offence or penalty (note: BNS 2023 replaced the IPC from July 1, 2024).",
        "CONSTITUTIONAL_CLAUSE": "This provision of the Constitution of India establishes a constitutional right, power, or restriction governing the State and citizens.",
        "INDIAN_STATUTE": "This Indian statutory provision defines legal rules, duties, exceptions, or penalties enacted by the legislature.",
        "CRIMINAL_OFFENCE_&_PUNISHMENT": "This criminal law section sets out the elements of an offence and the punishment (imprisonment, fine, or community service) prescribed under Indian law.",
        "CONSTITUTIONAL_RIGHT_&_PROVISION": "This constitutional provision defines a guaranteed right, constitutional remedy, or the scope of permitted statutory restrictions.",
        "STATUTORY_DEFINITION_&_EXCEPTION": "This statutory clause defines key legal terms, explanations, illustrations, or exceptions that narrow how the main section applies.",
        "JURISDICTION_&_PROCEDURE": "This procedural clause sets court jurisdiction, bail or trial rules, or the legal process that must be followed.",
        "INDEMNITY": f"This indemnification provision defines how legal liabilities and defense costs are allocated. Specifically, {party_str} promises to reimburse and defend the other party against legal claims, damages, and attorney fees arising from contract breaches or operational activities.",
        "CONFIDENTIALITY": f"This confidentiality covenant protects proprietary business information from disclosure. {party_str} is legally bound to keep proprietary disclosures secret and use them exclusively for authorized contract purposes.",
        "TERMINATION": "This clause establishes the formal exit procedures for ending this contract. It specifies the conditions required to cancel the agreement, required advance notice, and whether a cure period is granted to fix contract defaults.",
        "GOVERNING_LAW": "This choice of law clause designates which jurisdiction's courts and statutory laws govern any legal dispute. The parties agree to submit exclusively to these courts, avoiding cross-jurisdictional conflicts.",
        "NON_COMPETE": f"This restrictive covenant limits post-employment or post-business competitive activities for {party_str}. Note that under Section 27 of the Indian Contract Act, 1872, post-employment non-compete clauses face strict legal scrutiny in India.",
        "PAYMENT": "This financial clause sets the binding monetary terms. It details the payment schedule, invoicing procedures, acceptable payment methods, and any interest penalties for late payments.",
        "LIABILITY": "This limitation of liability clause restricts monetary damages if a legal breach occurs. It typically excludes consequential or indirect damages and caps total liability to protect against excessive lawsuits.",
        "FORCE_MAJEURE": "This force majeure clause excuses performance failures caused by unforeseeable emergencies beyond human control, such as natural disasters, war, strikes, or governmental restrictions.",
        "SEVERABILITY": "This severability provision ensures contract continuity. If a judge or arbitrator strikes down any single clause as invalid, all remaining clauses continue in full legal force.",
    }
    return intros.get(
        cat_upper,
        f"This {category or 'legal'} provision establishes binding terms and requirements that apply to {party_str}.",
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
    amounts_match = re.findall(
        r"(?:[\$₹€£]\s*|Rs\.?\s*|INR\s*)[\d,]+(?:\.\d{2})?(?:\s*(?:lakhs?|crores?))?",
        original_text,
        re.IGNORECASE,
    )
    imprisonment_match = re.findall(
        r"\b(?:imprisonment for life|death|\d+\s+years?|(?:one|two|three|five|seven|ten|fourteen)\s+years?|community service)\b",
        original_text,
        re.IGNORECASE,
    )

    details: list[str] = []
    if days_match:
        unique_days = list(dict.fromkeys(days_match))
        details.append(
            f"Specified timelines include notice or compliance windows of {', '.join(unique_days)} days."
        )
    if amounts_match:
        unique_amounts = list(dict.fromkeys(a.strip() for a in amounts_match))
        details.append(
            f"Monetary figures or fines noted in the text include {', '.join(unique_amounts)}."
        )
    if imprisonment_match:
        unique_terms = list(dict.fromkeys(t.strip() for t in imprisonment_match))
        details.append(
            f"Prescribed penalties mentioned include {', '.join(unique_terms)}."
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
