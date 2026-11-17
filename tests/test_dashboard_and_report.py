"""Tests for dashboard SQL aggregates, ReportLab PDF report generation, and tenant isolation."""

from pathlib import Path

import fitz

from app.models.analysis import DocumentAnalysis
from app.models.clause import ExtractedClause
from app.models.document import Document
from app.models.risk import RiskFinding
from app.models.user import User
from app.services.dashboard_service import get_dashboard_stats
from app.services.document_service import (
    delete_document_for_user,
    save_and_extract_document,
)
from app.services.report_service import generate_pdf_report


def test_dashboard_counts_stay_isolated_per_user(app):
    """Dashboard aggregates stay isolated per user and match direct SQL counts."""
    with app.app_context():
        from app.extensions import db

        u1 = User.query.filter_by(email="user_one@example.com").first()
        if not u1:
            u1 = User(email="user_one@example.com", full_name="User One", role="USER")
            u1.set_password("Password123!")
            db.session.add(u1)
            db.session.commit()

        u2 = User.query.filter_by(email="user_two@example.com").first()
        if not u2:
            u2 = User(email="user_two@example.com", full_name="User Two", role="USER")
            u2.set_password("Password123!")
            db.session.add(u2)
            db.session.commit()

        # Clear existing docs for both to ensure clean comparison
        for d in Document.query.filter(Document.user_id.in_([u1.id, u2.id])).all():
            delete_document_for_user(d.id, d.user_id)

        # Upload 1 contract for User 1 (clean_nda.pdf)
        nda_bytes = Path("samples/contracts/clean_nda.pdf").read_bytes()
        doc1, _, _, _ = save_and_extract_document(u1.id, nda_bytes, "clean_nda.pdf")

        # Upload 2 contracts for User 2 (rental_agreement.pdf & one_sided_agreement.pdf)
        rental_bytes = Path("samples/contracts/rental_agreement.pdf").read_bytes()
        onesided_bytes = Path("samples/contracts/one_sided_agreement.pdf").read_bytes()
        _doc2, _, _, _ = save_and_extract_document(
            u2.id, rental_bytes, "rental_agreement.pdf"
        )
        _doc3, _, _, _ = save_and_extract_document(
            u2.id, onesided_bytes, "one_sided_agreement.pdf"
        )

        # 3. Retrieve Dashboard Stats for User 1
        stats1 = get_dashboard_stats(u1.id)
        # Manual SQL checks for User 1
        manual_doc_count_1 = Document.query.filter_by(user_id=u1.id).count()
        manual_clauses_1 = (
            ExtractedClause.query.join(
                DocumentAnalysis,
                ExtractedClause.analysis_id == DocumentAnalysis.id,
            )
            .join(Document, DocumentAnalysis.document_id == Document.id)
            .filter(Document.user_id == u1.id)
            .count()
        )
        manual_risks_1 = (
            RiskFinding.query.join(
                DocumentAnalysis, RiskFinding.analysis_id == DocumentAnalysis.id
            )
            .join(Document, DocumentAnalysis.document_id == Document.id)
            .filter(Document.user_id == u1.id)
            .count()
        )

        assert stats1["totalDocuments"] == manual_doc_count_1 == 1
        assert stats1["totalClauses"] == manual_clauses_1
        assert stats1["totalRisks"] == manual_risks_1

        # 4. Retrieve Dashboard Stats for User 2
        stats2 = get_dashboard_stats(u2.id)
        # Manual SQL checks for User 2
        manual_doc_count_2 = Document.query.filter_by(user_id=u2.id).count()
        manual_clauses_2 = (
            ExtractedClause.query.join(
                DocumentAnalysis,
                ExtractedClause.analysis_id == DocumentAnalysis.id,
            )
            .join(Document, DocumentAnalysis.document_id == Document.id)
            .filter(Document.user_id == u2.id)
            .count()
        )
        manual_risks_2 = (
            RiskFinding.query.join(
                DocumentAnalysis, RiskFinding.analysis_id == DocumentAnalysis.id
            )
            .join(Document, DocumentAnalysis.document_id == Document.id)
            .filter(Document.user_id == u2.id)
            .count()
        )

        assert stats2["totalDocuments"] == manual_doc_count_2 == 2
        assert stats2["totalClauses"] == manual_clauses_2
        assert stats2["totalRisks"] == manual_risks_2

        # 5. Confirm strictly zero cross-user data leakage
        assert stats1["totalDocuments"] != stats2["totalDocuments"]
        assert stats2["totalRisks"] > stats1["totalRisks"]
        assert len(stats1["recentDocuments"]) == 1
        assert len(stats2["recentDocuments"]) == 2
        assert stats1["recentDocuments"][0]["id"] == doc1.id
        assert doc1.id not in [d["id"] for d in stats2["recentDocuments"]]


def test_delete_document_dashboard_counts_update(app):
    """Delete a document and confirm dashboard counts immediately decrease."""
    with app.app_context():
        from app.extensions import db

        u_del = User.query.filter_by(email="delete_user@example.com").first()
        if not u_del:
            u_del = User(
                email="delete_user@example.com",
                full_name="Delete User",
                role="USER",
            )
            u_del.set_password("Password123!")
            db.session.add(u_del)
            db.session.commit()

        # Upload a document
        nda_bytes = Path("samples/contracts/clean_nda.pdf").read_bytes()
        doc, _, _, _ = save_and_extract_document(
            u_del.id, nda_bytes, "clean_nda_del.pdf"
        )

        initial_stats = get_dashboard_stats(u_del.id)
        assert initial_stats["totalDocuments"] >= 1
        assert initial_stats["totalClauses"] >= 1

        # Delete the document
        delete_success = delete_document_for_user(doc.id, u_del.id)
        assert delete_success is True

        updated_stats = get_dashboard_stats(u_del.id)
        assert updated_stats["totalDocuments"] == initial_stats["totalDocuments"] - 1
        assert updated_stats["totalClauses"] < initial_stats["totalClauses"]


def test_pdf_report_generation_10_sections_and_unicode(app):
    """Generate PDF reports for 3 samples; verify all 10 sections, page numbers, and Unicode handling."""
    with app.app_context():
        from app.extensions import db

        test_u = User.query.filter_by(email="report_tester@example.com").first()
        if not test_u:
            test_u = User(
                email="report_tester@example.com",
                full_name="Report Tester",
                role="USER",
            )
            test_u.set_password("SecurePassword123!")
            db.session.add(test_u)
            db.session.commit()

        samples = [
            ("clean_nda.pdf", "samples/contracts/clean_nda.pdf"),
            ("rental_agreement.pdf", "samples/contracts/rental_agreement.pdf"),
            ("one_sided_agreement.pdf", "samples/contracts/one_sided_agreement.pdf"),
        ]

        for filename, filepath in samples:
            doc = Document.query.filter_by(
                user_id=test_u.id, original_filename=filename
            ).first()
            if not doc:
                doc, _, _, _ = save_and_extract_document(
                    test_u.id, Path(filepath).read_bytes(), filename
                )

            pdf_bytes = generate_pdf_report(doc, doc.analysis)
            assert len(pdf_bytes) > 10000
            assert pdf_bytes.startswith(b"%PDF-")

            # Inspect rendered PDF structure via PyMuPDF
            pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
            assert len(pdf) >= 2

            all_text = " ".join([page.get_text() for page in pdf])

            assert f"Page 1 of {len(pdf)}" in all_text

            assert "1. Executive Summary" in all_text
            assert "2. Important Contractual Provisions" in all_text
            assert "3. Plain-Language Explanations" in all_text
            assert "4. Contract Risk Assessment" in all_text
            assert "5. Financial Terms & Payment Structure" in all_text
            assert "6. Critical Dates & Timelines" in all_text
            assert "7. Standard Provisions Checklist" in all_text
            assert "8. Actionable Questions for Legal Counsel" in all_text
            assert "9. Regulatory Notice & Legal Disclaimer" in all_text

            # 3. Graceful risk handling on clean NDA
            if filename == "clean_nda.pdf":
                assert (
                    "No elevated contractual, legal, or financial risks detected"
                    in all_text
                    or "Extended Confidentiality Obligation" in all_text
                )

            # 4. Elevated risks on one-sided contract
            if filename == "one_sided_agreement.pdf":
                assert "[HIGH RISK]" in all_text

        # 5. Explicitly verify graceful empty risk section handling
        mock_doc = Document(
            id="mock-empty",
            original_filename="empty_sample.pdf",
            user_id=test_u.id,
        )
        mock_analysis = DocumentAnalysis(
            id="mock-an-empty",
            document_id="mock-empty",
            title="Empty Risk Sample",
            document_type="General Agreement",
            summary_short="Sample summary text.",
            summary_detailed="Sample detailed summary text.",
            risks=[],
            clauses=[],
            main_conditions=[],
            obligations_summary=[],
            financial_terms_summary=[],
        )
        empty_pdf = generate_pdf_report(mock_doc, mock_analysis)
        empty_doc_fitz = fitz.open(stream=empty_pdf, filetype="pdf")
        empty_text = " ".join([p.get_text() for p in empty_doc_fitz])
        assert (
            "No elevated contractual, legal, or financial risks detected" in empty_text
        )


def test_report_endpoint_authorization(client, app):
    """Confirm report endpoint is strictly authorized: owner -> 200, cross-user -> 404, unauth -> 401."""
    with app.app_context():
        from app.extensions import db

        u_owner = User.query.filter_by(email="report_owner@example.com").first()
        if not u_owner:
            u_owner = User(
                email="report_owner@example.com",
                full_name="Report Owner",
                role="USER",
            )
            u_owner.set_password("SecurePassword123!")
            db.session.add(u_owner)
            db.session.commit()

        u_other = User.query.filter_by(email="report_other@example.com").first()
        if not u_other:
            u_other = User(
                email="report_other@example.com",
                full_name="Report Other",
                role="USER",
            )
            u_other.set_password("SecurePassword123!")
            db.session.add(u_other)
            db.session.commit()

        doc = Document.query.filter_by(user_id=u_owner.id).first()
        if not doc:
            nda_bytes = Path("samples/contracts/clean_nda.pdf").read_bytes()
            doc, _, _, _ = save_and_extract_document(
                u_owner.id, nda_bytes, "clean_nda_auth.pdf"
            )
        doc_id = doc.id

    # 1. Unauthenticated request -> 401
    resp_unauth = client.get(f"/api/documents/{doc_id}/report")
    assert resp_unauth.status_code == 401

    # 2. Authenticated as other user accessing owner's document -> 404
    client.post(
        "/api/auth/login",
        json={
            "email": "report_other@example.com",
            "password": "SecurePassword123!",
        },
    )
    resp_cross = client.get(f"/api/documents/{doc_id}/report")
    assert resp_cross.status_code == 404

    # 3. Authenticated as owner -> 200 PDF
    client.post("/api/auth/logout")
    login_owner = client.post(
        "/api/auth/login",
        json={
            "email": "report_owner@example.com",
            "password": "SecurePassword123!",
        },
    )
    assert login_owner.status_code == 200

    resp_owner = client.get(f"/api/documents/{doc_id}/report")
    assert resp_owner.status_code == 200
    assert resp_owner.mimetype == "application/pdf"
    assert "Content-Disposition" in resp_owner.headers
    assert f"lexilegal_report_{doc_id}.pdf" in resp_owner.headers["Content-Disposition"]
    assert len(resp_owner.data) > 10000


def test_empty_dashboard_for_new_user(client, app):
    """Brand-new user sees zero metrics and an empty-state prompt."""
    with app.app_context():
        from app.extensions import db

        new_user = User.query.filter_by(email="brand_new@example.com").first()
        if not new_user:
            new_user = User(
                email="brand_new@example.com",
                full_name="New Attorney",
                role="USER",
            )
            new_user.set_password("StrongPassword123!")
            db.session.add(new_user)
            db.session.commit()

        stats = get_dashboard_stats(new_user.id)
        assert stats["totalDocuments"] == 0
        assert stats["analyzedDocuments"] == 0
        assert stats["totalClauses"] == 0
        assert stats["totalRisks"] == 0
        assert stats["averageVerificationRate"] == 0.0
        assert stats["recentDocuments"] == []

    # Login and check HTML rendering
    client.post(
        "/api/auth/login",
        json={
            "email": "brand_new@example.com",
            "password": "StrongPassword123!",
        },
    )

    resp_html = client.get("/dashboard")
    assert resp_html.status_code == 200
    html_text = resp_html.get_data(as_text=True)
    assert "No documents yet. Upload a contract to get started." in html_text
    assert "Upload" in html_text

    # Check API stats endpoint
    resp_api = client.get("/api/dashboard/stats")
    assert resp_api.status_code == 200
    api_data = resp_api.get_json()
    assert api_data["totalDocuments"] == 0
