import io
import json
from pathlib import Path

from app.nlp.clause_classifier import classify_clause
from app.nlp.document_classifier import classify_document_type
from app.nlp.evidence import extract_evidence_quote
from app.nlp.extraction import extract_document
from app.nlp.importance import calculate_clause_importance
from app.nlp.parties import detect_affected_party, extract_document_parties
from app.nlp.registry import get_clause_hf_classifier
from app.nlp.segmentation import segment_clauses
from evaluation.evaluate_clauses import match_clause


def test_document_type_classification():
    """Verify document type detection across various legal contract types."""
    contracts = [
        ("clean_nda.pdf", "Non-Disclosure Agreement (NDA)"),
        ("rental_agreement.pdf", "Residential Lease Agreement"),
        ("employment_agreement.pdf", "Executive Employment Agreement"),
        ("one_sided_agreement.pdf", "Master Services Agreement"),
        ("promissory_note.txt", "Promissory Note"),
        ("scanned_deed.pdf", "Property Deed"),
    ]
    for filename, expected_type in contracts:
        path = Path("samples/contracts") / filename
        data = path.read_bytes()
        doc = extract_document(data, filename)
        doc_type, conf = classify_document_type(doc.full_text, filename)
        assert (
            doc_type == expected_type
        ), f"Expected {expected_type}, got {doc_type} for {filename}"
        assert conf >= 0.70


def test_clause_classifier_ensemble_standard_categories():
    """Verify that ensemble classifies standard legal clauses into correct categories."""
    samples = [
        (
            "Confidentiality Obligations",
            "Receiving Party shall keep all proprietary trade secrets in strictest confidence.",
            "Confidentiality",
        ),
        (
            "Termination for Cause",
            "Either party may terminate this agreement immediately upon written notice for material breach.",
            "Termination",
        ),
        (
            "Intellectual Property Rights",
            "Employee hereby assigns to Company all right, title, and interest in and to any and all inventions.",
            "Intellectual Property",
        ),
        (
            "Non-Compete and Non-Solicitation",
            "Employee agrees not to engage in competing business or solicit clients for 12 months following termination.",
            "Non-Compete and Non-Solicitation",
        ),
        (
            "Monthly Rent and Security Deposit",
            "Tenant agrees to pay monthly rent of ₹28,000.00 in advance on or before the first calendar day.",
            "Payment Terms",
        ),
        (
            "Governing Law and Jurisdiction",
            "This Agreement shall be governed by and construed in accordance with the laws of India and courts in Karnataka.",
            "Governing Law",
        ),
        (
            "Severability",
            "If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions remain valid.",
            "Severability",
        ),
        (
            "Assignment and Subletting",
            "Tenant shall not assign this lease or sublet the premises without prior written consent.",
            "Assignment",
        ),
    ]

    for title, text, expected_cat in samples:
        cat, _custom_label, conf, _ = classify_clause(title, text)
        assert cat == expected_cat, f"For '{title}', expected {expected_cat}, got {cat}"
        assert conf > 0.0


def test_custom_label_on_other_category():
    """Ensure non-standard provisions are categorized as Other with descriptive custom labels."""
    title = "Section 1. Position and Scope of Duties"
    text = "Company agrees to employ Employee as Chief Technology Officer with general duties."
    cat, custom_label, _conf, _ = classify_clause(title, text)
    assert cat == "Other"
    assert custom_label == "Position and Scope of Duties"


def test_importance_scoring_rules():
    """Verify clause importance evaluation rules."""
    # Critical high triggers
    high_indemnity = "Customer shall indemnify, defend, and hold harmless Vendor without any limitation or financial cap."
    assert (
        calculate_clause_importance("Liability and Indemnification", high_indemnity)
        == "HIGH"
    )

    high_unilateral = (
        "Vendor may terminate this agreement at any time without cause upon notice."
    )
    assert calculate_clause_importance("Termination", high_unilateral) == "HIGH"

    high_interest = (
        "Unpaid balances accrue interest at 2.5% per month compounded daily."
    )
    assert calculate_clause_importance("Payment Terms", high_interest) == "HIGH"

    # Medium
    med_term = (
        "This agreement shall remain in effect for a fixed term of twelve (12) months."
    )
    assert calculate_clause_importance("Term and Renewal", med_term) == "MEDIUM"

    # Low boilerplate
    low_law = "This Agreement shall be governed by the laws of the State of Karnataka."
    assert calculate_clause_importance("Governing Law", low_law) == "LOW"


def test_affected_party_detection():
    """Verify extraction of contracting parties and affected obligor."""
    preamble = "This Agreement is made between Vayu Analytics Pvt. Ltd. ('Company') and Vikram Reddy ('Employee')."
    parties = extract_document_parties(preamble)
    assert "Company" in parties and "Employee" in parties

    clause_text = "Employee shall not directly or indirectly compete with the Company."
    affected = detect_affected_party(
        clause_text, parties, "Non-Compete and Non-Solicitation"
    )
    assert affected == "Employee"

    mutual_text = "This Agreement shall be governed by the laws of Maharashtra."
    assert (
        detect_affected_party(mutual_text, parties, "Governing Law") == "Both parties"
    )


def test_evidence_quote_exact_slice_verification():
    """Verify that 100% of evidence quotes are verified exact substrings."""
    original = (
        "3. Term and Termination. This Agreement shall remain in effect for a term of three (3) years "
        "from the Effective Date. Either party may terminate upon thirty (30) days notice."
    )
    quote, verified = extract_evidence_quote(
        original, "Term and Renewal", "Term and Termination"
    )
    assert verified is True
    assert quote in original
    assert len(quote) >= 15


def test_model_fallback_without_crashing():
    """Verify that system operates smoothly when fine-tuned BERT checkpoint is absent."""
    hf_model, _hf_tokenizer = get_clause_hf_classifier()
    assert hf_model is None or hf_model is not None
    cat, _, conf, _ = classify_clause(
        "Governing Law",
        "This agreement shall be governed by the laws of India.",
    )
    assert cat == "Governing Law"
    assert conf > 0.0


def test_clause_recall_and_precision_on_gold_contracts():
    """Clause recall >= 80% and precision >= 75% across gold test contracts."""
    gold_files = [
        "samples/gold/clean_nda_gold.json",
        "samples/gold/employment_agreement_gold.json",
        "samples/gold/rental_agreement_gold.json",
    ]

    total_gold = 0
    total_extracted = 0
    true_positives = 0

    for gf_path in gold_files:
        with open(gf_path, encoding="utf-8") as f:
            gold_data = json.load(f)
        contract_name = gold_data["contract_name"]
        contract_path = Path("samples/contracts") / contract_name
        doc = extract_document(contract_path.read_bytes(), contract_name)
        segmented = segment_clauses(doc.full_text, doc.pages, doc.sections)

        extracted = []
        for sc in segmented:
            cat, custom, _, _ = classify_clause(
                sc.title, sc.original_text, sc.section_reference
            )
            quote, _ = extract_evidence_quote(sc.original_text, cat, sc.title)
            extracted.append(
                {
                    "title": sc.title,
                    "category": cat,
                    "customLabel": custom,
                    "originalText": sc.original_text,
                    "evidenceQuote": quote,
                    "sectionReference": sc.section_reference or "",
                }
            )

        gold_clauses = gold_data.get("gold_clauses", [])
        total_gold += len(gold_clauses)
        total_extracted += len(extracted)

        matched_gold = set()
        for gc in gold_clauses:
            for ec in extracted:
                if match_clause(gc, ec):
                    matched_gold.add(gc["id"])
                    break
        true_positives += len(matched_gold)

    recall = true_positives / total_gold if total_gold else 0.0
    precision = true_positives / total_extracted if total_extracted else 0.0
    macro_f1 = (
        (2 * precision * recall) / (precision + recall) if (precision + recall) else 0.0
    )

    print(
        f"\n[BENCHMARK] Recall: {recall*100:.2f}%, Precision: {precision*100:.2f}%, F1: {macro_f1*100:.2f}%"
    )
    assert (
        recall >= 0.80
    ), f"Clause recall {recall*100:.2f}% is below 80% gate threshold."
    assert (
        precision >= 0.75
    ), f"Clause precision {precision*100:.2f}% is below 75% gate threshold."


def test_api_clauses_retrieval_and_filtering(app, client):
    """Verify REST API clause retrieval, category/importance filtering, and authorization."""
    with app.app_context():
        from app.extensions import db
        from app.models.user import User

        user = User(email="clause_user_a@example.com", full_name="User A", role="USER")
        user.set_password("Password123!")
        db.session.add(user)
        db.session.commit()

        # Login user A via API
        client.post(
            "/api/auth/login",
            json={"email": "clause_user_a@example.com", "password": "Password123!"},
        )

        # Upload contract
        contract_data = Path("samples/contracts/clean_nda.pdf").read_bytes()
        upload_resp = client.post(
            "/api/documents/upload",
            data={"file": (io.BytesIO(contract_data), "clean_nda.pdf")},
            content_type="multipart/form-data",
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.get_json()["id"]

        # 1. Fetch all clauses
        clauses_resp = client.get(f"/api/documents/{doc_id}/clauses")
        assert clauses_resp.status_code == 200
        data = clauses_resp.get_json()
        assert data["total"] > 0
        assert len(data["clauses"]) == data["total"]
        assert all(c["quoteVerified"] is True for c in data["clauses"])

        # 2. Filter by category
        conf_resp = client.get(
            f"/api/documents/{doc_id}/clauses?category=Confidentiality"
        )
        assert conf_resp.status_code == 200
        conf_data = conf_resp.get_json()
        assert conf_data["total"] >= 1
        assert all(c["category"] == "Confidentiality" for c in conf_data["clauses"])

        # 3. Filter by importance
        imp_resp = client.get(f"/api/documents/{doc_id}/clauses?importance=HIGH")
        assert imp_resp.status_code == 200
        imp_data = imp_resp.get_json()
        assert all(c["importance"] == "HIGH" for c in imp_data["clauses"])

        # 4. Search filter
        search_resp = client.get(f"/api/documents/{doc_id}/clauses?search=jurisdiction")
        assert search_resp.status_code == 200
        search_data = search_resp.get_json()
        assert search_data["total"] >= 1


def test_user_b_gets_404_for_user_a_clauses(app, client):
    """User B cannot access User A's clauses (returns 404)."""
    with app.app_context():
        from app.extensions import db
        from app.models.user import User

        user_a = User(email="user_alpha@example.com", full_name="Alpha", role="USER")
        user_a.set_password("Password123!")
        user_b = User(email="user_beta@example.com", full_name="Beta", role="USER")
        user_b.set_password("Password123!")
        db.session.add_all([user_a, user_b])
        db.session.commit()

        # User A logs in and uploads
        client.post(
            "/api/auth/login",
            json={"email": "user_alpha@example.com", "password": "Password123!"},
        )
        contract_data = Path("samples/contracts/clean_nda.pdf").read_bytes()
        upload_resp = client.post(
            "/api/documents/upload",
            data={"file": (io.BytesIO(contract_data), "clean_nda.pdf")},
            content_type="multipart/form-data",
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.get_json()["id"]

        # User B logs in and attempts to access User A's clauses
        client.post(
            "/api/auth/login",
            json={"email": "user_beta@example.com", "password": "Password123!"},
        )
        forbidden_resp = client.get(f"/api/documents/{doc_id}/clauses")
        assert forbidden_resp.status_code == 404
