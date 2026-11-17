import io
from pathlib import Path

from app.nlp.extraction import extract_document
from app.nlp.key_info import NOT_SPECIFIED, extract_contract_key_info
from app.nlp.segmentation import legal_sentence_tokenizer
from app.nlp.summarizer import generate_extractive_summary


def test_extractive_summary_verbatim_in_source():
    """Every sentence in an extractive summary must appear verbatim in full_text."""
    sample_files = [
        "clean_nda.pdf",
        "employment_agreement.pdf",
        "rental_agreement.pdf",
        "one_sided_agreement.pdf",
        "promissory_note.txt",
    ]

    for fname in sample_files:
        path = Path("samples/contracts") / fname
        doc = extract_document(path.read_bytes(), fname)
        summary = generate_extractive_summary(
            doc.full_text,
            doc.pages,
            document_type="Contract",
            parties=["Party A", "Party B"],
        )

        assert summary.summary_short, f"Empty short summary for {fname}"
        assert summary.summary_detailed, f"Empty detailed summary for {fname}"

        # Verify each sentence in short summary is verbatim in source text
        short_sentences = legal_sentence_tokenizer.tokenize(summary.summary_short)
        for s in short_sentences:
            s_clean = s.strip()
            if len(s_clean) >= 20:
                assert (
                    s_clean in doc.full_text
                ), f"Sentence '{s_clean}' in short summary of {fname} not found verbatim in source text!"

        # Verify each paragraph/sentence in detailed summary is verbatim in source text
        for paragraph in summary.summary_detailed.split("\n\n"):
            p_clean = paragraph.strip()
            if len(p_clean) >= 20:
                assert (
                    p_clean in doc.full_text
                ), f"Sentence '{p_clean}' in detailed summary of {fname} not found verbatim in source text!"


def test_absent_fields_default_to_not_specified():
    """Unstated fields should default to 'Not specified' with source_page=None."""
    path = Path("samples/contracts/clean_nda.pdf")
    doc = extract_document(path.read_bytes(), "clean_nda.pdf")
    info = extract_contract_key_info(doc.full_text, doc.pages)

    # Clean NDA specifies no money, no penalties, no renewal date, no end date
    assert info.contract_amount.value == NOT_SPECIFIED
    assert info.contract_amount.source_page is None
    assert info.penalties.value == NOT_SPECIFIED
    assert info.penalties.source_page is None
    assert info.renewal_date.value == NOT_SPECIFIED
    assert info.renewal_date.source_page is None
    assert info.end_date.value == NOT_SPECIFIED
    assert info.end_date.source_page is None
    assert "thirty (30) days" in info.notice_period.value


def test_key_facts_extraction_matching():
    """Verify exact ground truth extraction across employment, lease, and predatory samples."""
    # 1. Employment Agreement
    emp_path = Path("samples/contracts/employment_agreement.pdf")
    emp_doc = extract_document(emp_path.read_bytes(), "employment_agreement.pdf")
    emp_info = extract_contract_key_info(emp_doc.full_text, emp_doc.pages)

    assert "$185,000.00" in emp_info.contract_amount.value
    assert emp_info.contract_amount.source_page == 1
    assert "bi-weekly" in emp_info.payment_deadlines.value.lower()
    assert emp_info.payment_deadlines.source_page == 1
    assert "March 1, 2026" in emp_info.start_date.value
    assert "thirty (30) days" in emp_info.notice_period.value
    assert emp_info.penalties.value == NOT_SPECIFIED

    # 2. Residential Rental Agreement
    lease_path = Path("samples/contracts/rental_agreement.pdf")
    lease_doc = extract_document(lease_path.read_bytes(), "rental_agreement.pdf")
    lease_info = extract_contract_key_info(lease_doc.full_text, lease_doc.pages)

    assert "$2,400.00" in lease_info.contract_amount.value
    assert lease_info.contract_amount.source_page == 1
    assert (
        "first (1st) day" in lease_info.payment_deadlines.value
        or "calendar month" in lease_info.payment_deadlines.value
    )
    assert "August 1, 2026" in lease_info.start_date.value
    assert "July 31, 2027" in lease_info.end_date.value
    assert "$100.00" in lease_info.penalties.value

    # 3. One-Sided Predatory Agreement
    pred_path = Path("samples/contracts/one_sided_agreement.pdf")
    pred_doc = extract_document(pred_path.read_bytes(), "one_sided_agreement.pdf")
    pred_info = extract_contract_key_info(pred_doc.full_text, pred_doc.pages)

    assert "within three (3) calendar days" in pred_info.payment_deadlines.value
    assert "2.5% per month" in pred_info.penalties.value
    assert "one hundred eighty (180) days" in pred_info.notice_period.value
    assert "November 1, 2026" in pred_info.start_date.value
    assert pred_info.contract_amount.value == NOT_SPECIFIED


def test_important_dates_page_attribution():
    """Verify that important dates are detected with correct page attribution."""
    path = Path("samples/contracts/rental_agreement.pdf")
    doc = extract_document(path.read_bytes(), "rental_agreement.pdf")
    info = extract_contract_key_info(doc.full_text, doc.pages)

    assert len(info.important_dates) >= 1
    for item in info.important_dates:
        assert item["date"]
        assert item["page"] >= 1
        assert item["context"]


def test_api_key_info_and_summary_endpoints(app, client):
    """Verify API endpoints for key-info and summary serialization."""
    with app.app_context():
        from app.extensions import db
        from app.models.user import User

        user = User(
            email="summary_tester@example.com", full_name="Summary Tester", role="USER"
        )
        user.set_password("Password123!")
        db.session.add(user)
        db.session.commit()

        client.post(
            "/api/auth/login",
            json={"email": "summary_tester@example.com", "password": "Password123!"},
        )

        contract_bytes = Path("samples/contracts/employment_agreement.pdf").read_bytes()
        upload_resp = client.post(
            "/api/documents/upload",
            data={"file": (io.BytesIO(contract_bytes), "employment_agreement.pdf")},
            content_type="multipart/form-data",
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.get_json()["id"]

        # 1. GET /api/documents/<doc_id>/key-info
        key_resp = client.get(f"/api/documents/{doc_id}/key-info")
        assert key_resp.status_code == 200
        key_data = key_resp.get_json()
        assert key_data["contractAmount"] == "$185,000.00"
        assert key_data["paymentDeadlines"] == "bi-weekly"
        assert key_data["startDate"] == "March 1, 2026"
        assert key_data["penalties"] == NOT_SPECIFIED

        # 2. GET /api/documents/<doc_id>/summary
        sum_resp = client.get(f"/api/documents/{doc_id}/summary")
        assert sum_resp.status_code == 200
        sum_data = sum_resp.get_json()
        assert len(sum_data["shortSummary"]) > 20
        assert len(sum_data["detailedSummary"]) > 50
        assert "purpose" in sum_data


def test_user_b_gets_404_for_user_a_key_info(app, client):
    """User B cannot access User A's key-info or summary (returns 404)."""
    with app.app_context():
        from app.extensions import db
        from app.models.user import User

        user_a = User(email="owner_a@example.com", full_name="Owner A", role="USER")
        user_a.set_password("Password123!")
        user_b = User(
            email="intruder_b@example.com", full_name="Intruder B", role="USER"
        )
        user_b.set_password("Password123!")
        db.session.add_all([user_a, user_b])
        db.session.commit()

        # User A uploads
        client.post(
            "/api/auth/login",
            json={"email": "owner_a@example.com", "password": "Password123!"},
        )
        contract_bytes = Path("samples/contracts/clean_nda.pdf").read_bytes()
        up_resp = client.post(
            "/api/documents/upload",
            data={"file": (io.BytesIO(contract_bytes), "clean_nda.pdf")},
            content_type="multipart/form-data",
        )
        doc_id = up_resp.get_json()["id"]

        # User B logs in
        client.post(
            "/api/auth/login",
            json={"email": "intruder_b@example.com", "password": "Password123!"},
        )

        key_resp = client.get(f"/api/documents/{doc_id}/key-info")
        assert key_resp.status_code == 404

        sum_resp = client.get(f"/api/documents/{doc_id}/summary")
        assert sum_resp.status_code == 404
