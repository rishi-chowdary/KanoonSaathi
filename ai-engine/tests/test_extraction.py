from pathlib import Path
import io
import fitz
import docx
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)
VALID_HEADERS = {"X-Internal-Api-Key": settings.internal_api_key}
SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples" / "contracts"


def create_sample_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_multipage_pdf() -> bytes:
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 72), "Article 1. General Provisions\nFirst page content.")
    p2 = doc.new_page()
    p2.insert_text((50, 72), "Article 2. Confidentiality Terms\nSecond page content.")
    p3 = doc.new_page()
    p3.insert_text((50, 72), "Article 3. Termination\nThird page content.")
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_password_protected_pdf(password: str = "secret123") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Confidential Classified Contract Text")
    pdf_bytes = doc.tobytes(
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw="master_owner_pw",
        user_pw=password,
    )
    doc.close()
    return pdf_bytes


def create_sample_docx(paragraphs: list[str]) -> bytes:
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_extract_pdf_success():
    sample_text = (
        "EMPLOYMENT CONTRACT\n\n"
        "Article 1. Term of Employment\n"
        "The employee shall serve for two years.\n\n"
        "Section 2. Compensation\n"
        "Salary shall be paid bi-weekly."
    )
    pdf_bytes = create_sample_pdf(sample_text)

    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("contract.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["pages"]) == 1
    assert data["pages"][0]["page_number"] == 1
    assert data["pages"][0]["ocr_used"] is False
    assert "EMPLOYMENT CONTRACT" in data["pages"][0]["text"]
    assert any("1" in s["section_ref"] or "2" in s["section_ref"] for s in data["sections"])
    assert len(data["chunks"]) >= 1


def test_extract_multipage_pdf_page_numbers():
    pdf_bytes = create_multipage_pdf()

    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("multipage.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["pages"]) == 3

    # Verify strictly consecutive and correct 1-indexed page numbers
    page_numbers = [p["page_number"] for p in data["pages"]]
    assert page_numbers == [1, 2, 3]

    assert "First page content" in data["pages"][0]["text"]
    assert "Second page content" in data["pages"][1]["text"]
    assert "Third page content" in data["pages"][2]["text"]

    # Verify chunks reflect page ranges correctly
    for chunk in data["chunks"]:
        assert 1 <= chunk["page_start"] <= 3
        assert 1 <= chunk["page_end"] <= 3
        assert chunk["page_start"] <= chunk["page_end"]


def test_extract_scanned_pdf_ocr():
    scanned_file = SAMPLES_DIR / "scanned_deed.pdf"
    assert scanned_file.exists(), "samples/contracts/scanned_deed.pdf must exist"

    with open(scanned_file, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("scanned_deed.pdf", file_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["pages"]) >= 1
    page1 = data["pages"][0]
    assert page1["page_number"] == 1
    assert page1["ocr_used"] is True
    assert "DEED" in page1["text"].upper()


def test_extract_docx_success():
    paragraphs = [
        "SERVICE AGREEMENT",
        "Article 1. Scope of Services",
        "The provider shall render consulting services.",
        "Section 2. Fees and Payment",
        "Payment is due within thirty days of invoice.",
    ]
    docx_bytes = create_sample_docx(paragraphs)

    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("services.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["pages"]) >= 1
    assert data["pages"][0]["page_number"] == 1
    assert data["pages"][0]["ocr_used"] is False
    assert len(data["warnings"]) >= 1
    assert "DOCX" in data["warnings"][0]
    assert len(data["chunks"]) >= 1


def test_extract_txt_success():
    txt_content = (
        "CONFIDENTIALITY AGREEMENT\n\n"
        "Article I. Definitions\n"
        "The following terms shall have the meanings set forth herein.\n\n"
        "Section 2. Non-Disclosure Obligations\n"
        "Each party agrees not to disclose proprietary information.\n\n"
        "3. Governing Law\n"
        "This agreement shall be governed by the laws of California."
    ).encode("utf-8")

    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("agreement.txt", txt_content, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["pages"]) >= 1
    assert data["pages"][0]["page_number"] == 1
    assert data["language_guess"] == "en"
    assert len(data["sections"]) >= 2
    assert len(data["chunks"]) >= 1
    assert data["chunks"][0]["page_start"] == 1


def test_extract_empty_file():
    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "EMPTY_FILE"


def test_extract_corrupted_pdf():
    # File has %PDF- header but contains corrupt truncated syntax
    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("corrupted.pdf", b"%PDF-1.4\n%%EOF garbage corrupt bytes", "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "CORRUPTED_FILE"


def test_extract_password_protected_pdf():
    pdf_bytes = create_password_protected_pdf("SuperSecretPass")
    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("protected.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "PASSWORD_PROTECTED"
    assert "password" in data["detail"].lower()


def test_extract_wrong_magic_bytes_pdf():
    # Renamed text file claiming to be a PDF
    fake_pdf_bytes = b"Hello world, this is a plain text file pretending to be a PDF."
    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("fake.pdf", fake_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "CORRUPTED_FILE"
    assert "magic bytes" in data["detail"].lower()


def test_extract_wrong_magic_bytes_docx():
    # Renamed file without PK\x03\x04 zip header claiming to be docx
    fake_docx_bytes = b"Not a docx file at all"
    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("fake.docx", fake_docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "CORRUPTED_FILE"
    assert "magic bytes" in data["detail"].lower()


def test_extract_unsupported_type():
    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("script.py", b"print('hello')", "text/x-python")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "UNSUPPORTED_TYPE"


def test_extract_requires_api_key():
    response = client.post(
        "/internal/extract",
        files={"file": ("doc.txt", b"sample content", "text/plain")},
    )
    assert response.status_code == 401
