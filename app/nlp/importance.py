import re
from typing import Literal

# Categories that almost always carry high material impact for the signing party
HIGH_PRIORITY_CATEGORIES = {
    "Liability and Indemnification",
    "Non-Compete and Non-Solicitation",
    "Termination",
    "Intellectual Property",
}

# Standard boilerplate categories that are generally low material risk
LOW_PRIORITY_CATEGORIES = {
    "Governing Law",
    "Notices",
    "Severability",
}

# Critical trigger phrases that elevate a clause to HIGH importance regardless of category
CRITICAL_HIGH_TRIGGERS = [
    r"\buncapped\b",
    r"\bunlimited\s+indemnif",
    r"\bwithout\s+cause\b",
    r"\bcompounded\s+daily\b",
    r"\bsole\s+discretion\b",
    r"\bstrictly\s+prohibited\b",
    r"\bshall\s+not\s+directly\s+or\s+indirectly\b",
    r"\baccelerat(?:ion|e)\b",
    r"\bevict(?:ion)?\b",
    r"\bforfeit(?:ure|ed)?\b",
    r"\bautomatically\s+renew\b",
    r"\bin\s+no\s+event\s+shall\b",
    r"\bindemnify,\s+defend\b",
    r"\bhold\s+harmless\b",
    r"\bassigns\s+to\s+company\b",
    r"\bwithout\s+requiring\s+customer'?s\s+consent\b",
]

MONEY_REGEX = re.compile(
    r"(\$|€|£|₹|Rs\.?)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)"
)


def calculate_clause_importance(
    category: str,
    original_text: str,
    title: str = "",
) -> Literal["HIGH", "MEDIUM", "LOW"]:
    """Determine the importance level (HIGH, MEDIUM, LOW) of a legal clause.

    Combines category base weight, presence of unilateral/restrictive covenants,
    financial magnitude, and strong modal obligation verbs.
    """
    text_lower = original_text.lower()
    title_lower = title.lower()
    combined = f"{title_lower} {text_lower}"

    for trigger in CRITICAL_HIGH_TRIGGERS:
        if re.search(trigger, combined):
            return "HIGH"

    if category in HIGH_PRIORITY_CATEGORIES:
        return "HIGH"

    if category == "Payment Terms":
        # Rent, base salary, notes, or large fees are HIGH; incidental fee schedules are MEDIUM
        if any(
            k in combined
            for k in ["rent", "salary", "principal", "fee", "compensation", "interest"]
        ):
            matches = MONEY_REGEX.findall(original_text)
            if matches:
                return "HIGH"
            if "monthly" in combined or "annual" in combined:
                return "HIGH"
        return "MEDIUM"

    if category == "Assignment":
        # Strict subletting/assignment prohibitions are material
        if (
            "shall not assign" in text_lower
            or "sublet" in text_lower
            or "prohibit" in text_lower
        ):
            return "HIGH"
        return "MEDIUM"

    if category == "Confidentiality":
        # Strict secrecy obligations or trade secret assignments
        if (
            "strict" in text_lower
            or "secrecy" in text_lower
            or "injunctive relief" in text_lower
        ):
            return "HIGH"
        return "MEDIUM"

    if category == "Term and Renewal":
        # Automatic renewal or multi-year terms are MEDIUM; single-month leases are LOW
        if (
            "renew" in text_lower
            or "term of" in text_lower
            or "fixed term" in text_lower
        ):
            return "MEDIUM"
        return "LOW"

    if category in LOW_PRIORITY_CATEGORIES:
        return "LOW"

    if category == "Other":
        # Preamble, Property Description, Scope of Duties
        if "duties" in title_lower or "position" in title_lower:
            return "LOW"
        if "maintenance" in title_lower or "alterations" in title_lower:
            return "LOW"
        if "definitions" in title_lower:
            return "MEDIUM"
        return "LOW"

    return "MEDIUM"
