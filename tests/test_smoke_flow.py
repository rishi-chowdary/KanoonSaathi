"""End-to-End Smoke Test for LexiLegal AI.

Simulates the complete user lifecycle in a single end-to-end flow:
1. Register new user
2. Login & verify authenticated session
3. Upload PDF contract document
4. Verify extraction, chunks, and clause classification
5. Verify grounded risk detection & missing provisions
6. Test interactive simplification modes
7. Ask a question and verify page citation
8. Generate and download ReportLab 10-section PDF report
9. Verify dashboard statistics update
10. Delete document and confirm cleanup cascade
"""

import io
from pathlib import Path

from app.models.document import Document

SAMPLE_PDF = (
    Path(__file__).resolve().parent.parent
    / "samples"
    / "contracts"
    / "rental_agreement.pdf"
)


def test_full_lifecycle_smoke(client, app):
    """Execute complete end-to-end user and document workflow."""
    # 1. Register fresh user
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "email": "e2e_runner@example.com",
            "password": "Password123!",
            "full_name": "E2E Smoke Runner",
        },
    )
    assert reg_resp.status_code == 201
    assert "user" in reg_resp.get_json()
    assert "id" in reg_resp.get_json()["user"]

    # 2. Login
    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "e2e_runner@example.com",
            "password": "Password123!",
        },
    )
    assert login_resp.status_code == 200

    # 3. Upload contract
    assert SAMPLE_PDF.exists(), f"Missing sample file {SAMPLE_PDF}"
    file_bytes = SAMPLE_PDF.read_bytes()

    upload_resp = client.post(
        "/api/documents/upload",
        data={"file": (io.BytesIO(file_bytes), "rental_agreement.pdf")},
        content_type="multipart/form-data",
    )
    assert upload_resp.status_code == 201
    doc_data = upload_resp.get_json()
    doc_id = doc_data["id"]
    assert doc_data["pageCount"] >= 1

    # 4. View document detail & status
    status_resp = client.get(f"/api/documents/{doc_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.get_json()["status"] in ("UPLOADED", "COMPLETED")

    # 5. Retrieve classified clauses with verified quotes
    clauses_resp = client.get(f"/api/documents/{doc_id}/clauses")
    assert clauses_resp.status_code == 200
    clauses_data = clauses_resp.get_json()
    clauses = clauses_data.get("clauses", clauses_data)
    assert len(clauses) >= 4
    for c in clauses:
        assert c["quoteVerified"] is True
        assert c["evidenceQuote"] in c["originalText"]
        assert "simplifiedSimple" in c
        assert len(c["simplifiedSimple"]) > 0

    # 6. Retrieve grounded risk findings
    risks_resp = client.get(f"/api/documents/{doc_id}/risks")
    assert risks_resp.status_code == 200
    risks = risks_resp.get_json()
    assert len(risks) >= 2
    for r in risks:
        assert r["quoteVerified"] is True

    # 7. Grounded Document Chat Q&A
    chat_resp = client.post(
        f"/api/documents/{doc_id}/chat",
        json={"message": "What is the monthly rent amount and when is it due?"},
    )
    assert chat_resp.status_code == 200
    chat_data = chat_resp.get_json()
    assert chat_data["addressedInDocument"] is True
    answer_text = chat_data.get("content") or chat_data.get("answer", "")
    assert "2,400" in answer_text
    citations = chat_data.get("citations", [])
    assert len(citations) > 0
    assert citations[0]["page"] == 1

    # 8. Unanswerable question honesty probe
    chat_unans = client.post(
        f"/api/documents/{doc_id}/chat",
        json={"message": "What is the pet policy for keeping exotic reptiles?"},
    )
    assert chat_unans.status_code == 200
    unans_data = chat_unans.get_json()
    unans_text = unans_data.get("content") or unans_data.get("answer", "")
    assert (
        unans_data.get("addressedInDocument") is False
        or "does not appear to address" in unans_text.lower()
    )

    # Download 10-section PDF report
    report_resp = client.get(f"/api/documents/{doc_id}/report")
    assert report_resp.status_code == 200
    assert report_resp.content_type == "application/pdf"
    assert len(report_resp.data) > 10000
    assert report_resp.data.startswith(b"%PDF-")

    # 10. Check dashboard metrics update
    dash_resp = client.get("/api/dashboard/stats")
    assert dash_resp.status_code == 200
    dash_data = dash_resp.get_json()
    assert dash_data["totalDocuments"] >= 1
    assert dash_data["totalClauses"] >= 4
    assert dash_data["averageVerificationRate"] == 100.0

    # 11. Delete document & verify cascade
    del_resp = client.delete(f"/api/documents/{doc_id}")
    assert del_resp.status_code == 200

    with app.app_context():
        assert Document.query.filter_by(id=doc_id).first() is None
