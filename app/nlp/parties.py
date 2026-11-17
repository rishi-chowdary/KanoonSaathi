import re

from app.nlp.registry import get_spacy

# Common paired legal roles
ROLE_PAIRS = [
    ("Company", "Employee"),
    ("Employer", "Employee"),
    ("Landlord", "Tenant"),
    ("Disclosing Party", "Receiving Party"),
    ("Vendor", "Customer"),
    ("Provider", "Client"),
    ("Lender", "Borrower"),
    ("Grantor", "Grantee"),
]

ROLE_PATTERN = re.compile(
    r"\b(?:hereinafter\s+(?:referred\s+to\s+as\s+)?[\"“']?([A-Za-z\s]+)[\"”']?|\([\"“']?([A-Za-z\s]+)[\"”']?\))",
    re.IGNORECASE,
)


def extract_document_parties(preamble_text: str) -> list[str]:
    """Extract named contracting parties and their roles from contract preamble."""
    if not preamble_text:
        return ["Both parties"]

    found_roles: list[str] = []
    preamble_lower = preamble_text.lower()

    # Check for known role pairs
    for role_a, role_b in ROLE_PAIRS:
        has_a = role_a.lower() in preamble_lower
        has_b = role_b.lower() in preamble_lower
        if has_a and has_b:
            return [role_a, role_b]
        if has_a:
            found_roles.append(role_a)
        if has_b:
            found_roles.append(role_b)

    if found_roles:
        return list(dict.fromkeys(found_roles))

    # Look for capitalized entities with spaCy NER (PERSON, ORG)
    nlp = get_spacy()
    doc = nlp(preamble_text[:1000])
    entities = [ent.text.strip() for ent in doc.ents if ent.label_ in ("ORG", "PERSON")]
    if entities:
        # Deduplicate and return top 2
        unique = list(dict.fromkeys(entities))
        return unique[:2]

    return ["Both parties"]


def detect_affected_party(
    original_text: str,
    document_parties: list[str] | None = None,
    category: str = "",
) -> str:
    """Identify which party is primarily bound, restricted, or affected by a clause."""
    if not original_text:
        return "Both parties"

    text_lower = original_text.lower()

    # 1. Direct party role mentions in prominent subject positions
    parties = document_parties or [
        "Employee",
        "Tenant",
        "Customer",
        "Receiving Party",
        "Borrower",
        "Company",
        "Landlord",
        "Vendor",
        "Disclosing Party",
        "Lender",
    ]

    # Check for specific one-sided covenants
    if "employee shall" in text_lower or "employee agrees" in text_lower:
        return "Employee"
    if "tenant shall" in text_lower or "tenant agrees" in text_lower:
        return "Tenant"
    if "customer shall" in text_lower or "customer agrees" in text_lower:
        return "Customer"
    if "receiving party shall" in text_lower or "receiving party agrees" in text_lower:
        return "Receiving Party"
    if "company shall" in text_lower or "company agrees" in text_lower:
        return "Company"
    if "landlord shall" in text_lower or "landlord agrees" in text_lower:
        return "Landlord"
    if "vendor shall" in text_lower or "vendor agrees" in text_lower:
        return "Vendor"
    if "borrower shall" in text_lower or "borrower promises" in text_lower:
        return "Borrower"

    # Category defaults if clear
    if category == "Governing Law" or category == "Dispute Resolution":
        return "Both parties"
    if category == "Confidentiality" and "receiving party" in text_lower:
        return "Receiving Party"
    if category == "Non-Compete and Non-Solicitation":
        for p in ("Employee", "Contractor", "Customer"):
            if p.lower() in text_lower:
                return p
        return "Employee"

    # Match against provided document parties
    matched_parties = [p for p in parties if p.lower() in text_lower]
    if len(matched_parties) == 1:
        return matched_parties[0]
    elif len(matched_parties) > 1:
        # Check which one appears with modal verbs
        for p in matched_parties:
            if re.search(
                rf"\b{re.escape(p)}\s+(?:shall|must|agrees|warrants)\b",
                original_text,
                re.IGNORECASE,
            ):
                return p
        return "Both parties"

    return "Both parties"
