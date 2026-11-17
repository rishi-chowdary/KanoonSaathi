import io
from pathlib import Path

from app.extensions import db
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.user import User

SAMPLES_DIR = Path("samples/contracts")


def test_api_upload_valid_pdf(client, test_user, app):
    """Uploading a valid contract creates document and chunks in MySQL."""
    # 1. Login user
    client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )

    # 2. Upload clean_nda.pdf
    file_bytes = (SAMPLES_DIR / "clean_nda.pdf").read_bytes()
    data = {
        "file": (io.BytesIO(file_bytes), "clean_nda.pdf"),
    }
    response = client.post(
        "/api/documents/upload",
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    doc_json = response.json
    assert doc_json["originalFilename"] == "clean_nda.pdf"
    assert doc_json["fileType"] == "PDF"
    assert doc_json["pageCount"] == 2
    assert doc_json["status"] in ("EXTRACTED", "COMPLETED")
    doc_id = doc_json["id"]

    # 3. Verify chunks stored in MySQL
    with app.app_context():
        chunks = DocumentChunk.query.filter_by(document_id=doc_id).all()
        assert len(chunks) >= 2


def test_api_upload_duplicate_detection(client, test_user):
    """Uploading identical document twice by the same user is rejected."""
    client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )

    file_bytes = (SAMPLES_DIR / "promissory_note.txt").read_bytes()

    # First upload succeeds
    r1 = client.post(
        "/api/documents/upload",
        data={"file": (io.BytesIO(file_bytes), "promissory_note.txt")},
        content_type="multipart/form-data",
    )
    assert r1.status_code == 201

    # Second identical upload rejected
    r2 = client.post(
        "/api/documents/upload",
        data={"file": (io.BytesIO(file_bytes), "promissory_note.txt")},
        content_type="multipart/form-data",
    )
    assert r2.status_code == 400
    assert "already uploaded" in r2.json["error"]


def test_api_get_document_and_text(client, test_user):
    """Retrieve document metadata and page text via API."""
    client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )

    file_bytes = (SAMPLES_DIR / "clean_nda.pdf").read_bytes()
    up_resp = client.post(
        "/api/documents/upload",
        data={"file": (io.BytesIO(file_bytes), "clean_nda.pdf")},
        content_type="multipart/form-data",
    )
    doc_id = up_resp.json["id"]

    # Get single document
    get_resp = client.get(f"/api/documents/{doc_id}")
    assert get_resp.status_code == 200
    assert get_resp.json["id"] == doc_id

    # Get text
    text_resp = client.get(f"/api/documents/{doc_id}/text")
    assert text_resp.status_code == 200
    assert text_resp.json["pageCount"] == 2
    assert "NON-DISCLOSURE" in text_resp.json["fullText"]
    assert len(text_resp.json["pages"]) == 2


def test_document_ownership_isolation(client, test_user, app):
    """User B cannot view or delete User A's document (returns 404)."""
    # 1. Create second user
    with app.app_context():
        user_b = User(email="intruder@firm.com", full_name="Intruder Bob", role="USER")
        user_b.set_password("IntruderPass2026!")
        db.session.add(user_b)
        db.session.commit()

    # 2. Login as User A and upload
    client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )
    file_bytes = (SAMPLES_DIR / "clean_nda.pdf").read_bytes()
    up_resp = client.post(
        "/api/documents/upload",
        data={"file": (io.BytesIO(file_bytes), "clean_nda.pdf")},
        content_type="multipart/form-data",
    )
    doc_id = up_resp.json["id"]

    # 3. Switch login to User B
    client.post("/api/auth/logout")
    client.post(
        "/api/auth/login",
        json={"email": "intruder@firm.com", "password": "IntruderPass2026!"},
    )

    # 4. User B attempts to access User A's document -> 404
    get_resp = client.get(f"/api/documents/{doc_id}")
    assert get_resp.status_code == 404

    # 5. User B attempts to delete User A's document -> 404
    del_resp = client.delete(f"/api/documents/{doc_id}")
    assert del_resp.status_code == 404

    # Confirm document still exists in DB
    with app.app_context():
        doc = db.session.get(Document, doc_id)
        assert doc is not None


def test_delete_document_and_cascade(client, test_user, app):
    """Deleting a document cleans up database records and disk file."""
    client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )

    file_bytes = (SAMPLES_DIR / "rental_agreement.pdf").read_bytes()
    up_resp = client.post(
        "/api/documents/upload",
        data={"file": (io.BytesIO(file_bytes), "rental_agreement.pdf")},
        content_type="multipart/form-data",
    )
    doc_id = up_resp.json["id"]

    with app.app_context():
        doc = db.session.get(Document, doc_id)
        file_path = Path(doc.storage_path)
        assert file_path.exists()
        assert DocumentChunk.query.filter_by(document_id=doc_id).count() >= 1

    # Delete
    del_resp = client.delete(f"/api/documents/{doc_id}")
    assert del_resp.status_code == 200

    # Verify deleted from DB and disk
    with app.app_context():
        assert db.session.get(Document, doc_id) is None
        assert DocumentChunk.query.filter_by(document_id=doc_id).count() == 0
        assert not file_path.exists()
