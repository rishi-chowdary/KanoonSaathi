"""Expected-provisions checklist and missing-clause detector.

Compares extracted document clauses against document-type checklists using
keyword rules and SBERT prototype similarity, tagging omissions as
"Possible omission" and filtering out definitive legal claims.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Any

import numpy as np
import yaml

from app.nlp.registry import get_sbert
from app.nlp.risk_engine import soften_legal_claims

_CHECKLIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "expected_provisions.yaml",
)

# Document type normalization mapping
DOC_TYPE_MAPPING = {
    "bharatiya nyaya sanhita (bns) statute": "INDIAN_STATUTE",
    "indian penal code (ipc) statute": "INDIAN_STATUTE",
    "constitution of india": "INDIAN_STATUTE",
    "non-disclosure agreement": "NON_DISCLOSURE_AGREEMENT",
    "non-disclosure agreement (nda)": "NON_DISCLOSURE_AGREEMENT",
    "nda": "NON_DISCLOSURE_AGREEMENT",
    "confidentiality agreement": "NON_DISCLOSURE_AGREEMENT",
    "rental agreement": "LEASE_AGREEMENT",
    "lease agreement": "LEASE_AGREEMENT",
    "leave and license": "LEASE_AGREEMENT",
    "leave and license agreement": "LEASE_AGREEMENT",
    "commercial lease": "LEASE_AGREEMENT",
    "lease": "LEASE_AGREEMENT",
    "residential lease": "LEASE_AGREEMENT",
    "residential lease agreement": "LEASE_AGREEMENT",
    "employment agreement": "EMPLOYMENT_AGREEMENT",
    "executive employment agreement": "EMPLOYMENT_AGREEMENT",
    "employment contract": "EMPLOYMENT_AGREEMENT",
    "service agreement": "SERVICE_AGREEMENT",
    "services agreement": "SERVICE_AGREEMENT",
    "saas agreement": "SERVICE_AGREEMENT",
    "master services agreement": "SERVICE_AGREEMENT",
    "promissory note": "PROMISSORY_NOTE",
    "loan agreement": "PROMISSORY_NOTE",
}


@lru_cache(maxsize=1)
def load_expected_provisions() -> dict[str, Any]:
    if not os.path.exists(_CHECKLIST_PATH):
        return {}
    with open(_CHECKLIST_PATH, encoding="utf-8") as f:
        raw_checklists = yaml.safe_load(f) or {}
    return raw_checklists.get("document_types", {})


def normalize_document_type(doc_type_str: str) -> str:
    if not doc_type_str:
        return "GENERAL_CONTRACT"
    clean = doc_type_str.lower().strip()
    return DOC_TYPE_MAPPING.get(clean, "GENERAL_CONTRACT")


def check_keyword_presence(provision_id: str, combined_text: str) -> bool:
    """Check explicit keyword presence for key provisions."""
    combined_lower = combined_text.lower()

    keyword_rules = {
        "nda_exclusions": [
            r"\b(exclusions?|carve-outs?|public domain|publicly known|independently developed)\b"
        ],
        "nda_compelled_disclosure": [
            r"\b(subpoena|court order|compelled by law|legal process|judicial order)\b"
        ],
        "nda_return_destruction": [
            r"\b(return or destroy|destruction of materials|certify destruction|return all documents)\b"
        ],
        "nda_no_license": [
            r"\b(no license|neither party grants.*license|does not grant any patent)\b"
        ],
        "nda_remedies": [
            r"\b(injunction|injunctive relief|irreparable harm|equitable relief)\b"
        ],
        "lease_security_deposit": [
            r"\b(security deposit.*return|refund.*deposit|deposit.*escrow|itemized deductions?)\b"
        ],
        "lease_entry_notice": [
            r"\b(right of entry|enter the premises.*notice|24 hours.*notice|advance notice.*inspection)\b"
        ],
        "lease_maintenance": [
            r"\b(maintenance and repairs?|landlord shall maintain|structural repairs?|habitability)\b"
        ],
        "lease_cure_period": [
            r"\b(notice of default.*cure|opportunity to cure|grace period.*cure)\b"
        ],
        "emp_benefits_pto": [
            r"\b(health insurance|medical benefits?|paid time off|pto|vacation days?)\b"
        ],
        "emp_severance_termination": [
            r"\b(severance pay|termination without cause.*severance|definition of cause)\b"
        ],
        "emp_ip_carveouts": [
            r"\b(pre-existing inventions?|prior inventions?|personal time carve-out|excluded inventions?)\b"
        ],
        "service_sow_acceptance": [
            r"\b(statement of work|acceptance criteria|formal inspection|acceptance testing)\b"
        ],
        "service_ip_ownership": [
            r"\b(client owns|ownership of deliverables|assignment of custom deliverables)\b"
        ],
        "service_sla_uptime": [
            r"\b(service level agreement|uptime guarantee|service credits?|99\\.[0-9]%)\b"
        ],
        "service_force_majeure": [
            r"\b(force majeure|acts of god|events beyond reasonable control)\b"
        ],
        "note_prepayment": [
            r"\b(prepay.*without penalty|prepayment penalty|right to prepay)\b"
        ],
        "note_grace_period": [
            r"\b(grace period.*acceleration|written notice.*prior to acceleration|cure.*default)\b"
        ],
    }

    patterns = keyword_rules.get(provision_id, [])
    return any(re.search(pat, combined_lower) for pat in patterns)


def detect_missing_provisions(
    clauses: list[Any],
    document_type: str = "",
    full_text: str = "",
) -> list[dict[str, Any]]:
    """Return expected provisions missing from the document, labeled 'Possible omission'."""
    checklists = load_expected_provisions()
    checklist_key = normalize_document_type(document_type)

    doc_checklist = checklists.get(checklist_key)
    if not doc_checklist:
        # Fallback to general or return empty
        return []

    expected_list = doc_checklist.get("expected_provisions", [])
    if not expected_list:
        return []

    sbert = get_sbert()

    # Concatenate all clause texts and titles for presence checks
    clause_texts = [
        f"{getattr(c, 'title', '')}: {getattr(c, 'original_text', '')}" for c in clauses
    ]
    combined_corpus = full_text or " ".join(clause_texts)

    clause_embs = None
    if clause_texts:
        clause_embs = sbert.encode(clause_texts, normalize_embeddings=True)

    missing_findings: list[dict[str, Any]] = []

    for provision in expected_list:
        prov_id = provision["provision_id"]
        clause_name = provision["clause_name"]
        risk_level = provision["risk_level"]
        category = provision["category"]
        why_it_matters = provision["why_it_matters"]
        typical_provision = provision["typical_provision"]
        prototypes = provision.get("prototype_phrases", [])

        if check_keyword_presence(prov_id, combined_corpus):
            continue

        is_present_semantically = False
        if clause_embs is not None and len(clause_embs) > 0 and prototypes:
            proto_embs = sbert.encode(prototypes, normalize_embeddings=True)
            sim_matrix = np.dot(proto_embs, clause_embs.T)
            max_sim = float(np.max(sim_matrix))

            if max_sim >= 0.52:
                is_present_semantically = True

        if not is_present_semantically:
            missing_findings.append(
                {
                    "provision_id": prov_id,
                    "clause_name": soften_legal_claims(clause_name),
                    "category": category,
                    "why_it_matters": soften_legal_claims(why_it_matters),
                    "typical_provision": soften_legal_claims(typical_provision),
                    "risk_level": risk_level,
                    "label": "Possible omission",
                }
            )

    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    missing_findings.sort(key=lambda x: severity_order.get(x["risk_level"], 3))

    return missing_findings
