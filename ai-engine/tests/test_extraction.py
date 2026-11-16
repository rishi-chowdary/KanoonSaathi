import io
import fitz
import docx
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)
VALID_HEADERS = {"X-Internal-Api-Key": settings.internal_api_key}


def create_sample_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_sample_docx(paragraphs: list[str]) -> bytes:
    doc = docx.Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


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
    assert data["language_guess"] == "en"
    assert len(data["sections"]) >= 2
    assert len(data["chunks"]) >= 1
    assert data["chunks"][0]["page_start"] == 1


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
    assert "EMPLOYMENT CONTRACT" in data["pages"][0]["text"]
    assert any(s["section_ref"] in ["Section 1", "Section 2", "1", "2"] for s in data["sections"])
    assert len(data["chunks"]) >= 1


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
    assert len(data["warnings"]) >= 1
    assert "DOCX" in data["warnings"][0]
    assert len(data["chunks"]) >= 1


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
    response = client.post(
        "/internal/extract",
        headers=VALID_HEADERS,
        files={"file": ("corrupted.pdf", b"%PDF-1.4 garbage corrupt content", "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "CORRUPTED_FILE"


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
