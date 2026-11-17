from pathlib import Path

import pytest

from app.nlp.extraction import compute_sha256, extract_document, validate_file

SAMPLES_DIR = Path("samples/contracts")


def test_extract_clean_nda_pdf():
    """Extract clean NDA PDF via PyMuPDF."""
    file_bytes = (SAMPLES_DIR / "clean_nda.pdf").read_bytes()
    res = extract_document(file_bytes, "clean_nda.pdf")

    assert res.page_count == 2
    assert not res.is_scanned
    assert len(res.full_text) > 200
    assert "NON-DISCLOSURE" in res.full_text
    assert len(res.sections) >= 3


def test_extract_rental_agreement_pdf():
    """Extract multi-page rental agreement PDF."""
    file_bytes = (SAMPLES_DIR / "rental_agreement.pdf").read_bytes()
    res = extract_document(file_bytes, "rental_agreement.pdf")

    assert res.page_count == 2
    assert not res.is_scanned
    assert "LEASE AGREEMENT" in res.full_text
    assert len(res.sections) >= 6


def test_extract_service_agreement_docx():
    """Extract Microsoft Word DOCX contract."""
    file_bytes = (SAMPLES_DIR / "service_agreement.docx").read_bytes()
    res = extract_document(file_bytes, "service_agreement.docx")

    assert res.page_count >= 1
    assert "MASTER SERVICES AGREEMENT" in res.full_text
    assert len(res.sections) >= 3


def test_extract_promissory_note_txt():
    """Extract plain text promissory note."""
    file_bytes = (SAMPLES_DIR / "promissory_note.txt").read_bytes()
    res = extract_document(file_bytes, "promissory_note.txt")

    assert res.page_count >= 1
    assert "PROMISSORY NOTE" in res.full_text
    assert len(res.sections) >= 3


def test_extract_scanned_pdf_with_ocr():
    """Extract scanned image-based contract using Tesseract OCR fallback."""
    file_bytes = (SAMPLES_DIR / "scanned_deed.pdf").read_bytes()
    res = extract_document(file_bytes, "scanned_deed.pdf")

    assert res.is_scanned
    assert res.page_count == 1
    assert len(res.full_text) > 50
    assert "DEED" in res.full_text.upper()


def test_corrupted_file_rejection():
    """Corrupted binary files must be rejected with descriptive error."""
    file_bytes = (SAMPLES_DIR / "corrupted_contract.pdf").read_bytes()
    with pytest.raises(ValueError, match="Unable to parse PDF|Corrupted"):
        extract_document(file_bytes, "corrupted_contract.pdf")


def test_empty_file_rejection():
    """Zero-byte files must be rejected immediately."""
    file_bytes = (SAMPLES_DIR / "empty_contract.pdf").read_bytes()
    with pytest.raises(ValueError, match="File is empty"):
        validate_file(file_bytes, "empty_contract.pdf")


def test_fake_extension_rejection():
    """Executables disguised as PDF must be rejected by magic bytes inspection."""
    file_bytes = (SAMPLES_DIR / "malicious_renamed.exe.pdf").read_bytes()
    with pytest.raises(ValueError, match="Corrupted PDF"):
        validate_file(file_bytes, "malicious_renamed.exe.pdf")


def test_oversized_file_rejection():
    """Files exceeding 10MB limit must be rejected."""
    oversized = b"%PDF-1.4 " + b"x" * (10 * 1024 * 1024 + 10)
    with pytest.raises(ValueError, match="10MB"):
        validate_file(oversized, "huge.pdf")


def test_sha256_reproducibility():
    """SHA-256 digest calculation is deterministic."""
    file_bytes = (SAMPLES_DIR / "clean_nda.pdf").read_bytes()
    h1 = compute_sha256(file_bytes)
    h2 = compute_sha256(file_bytes)
    assert h1 == h2
    assert len(h1) == 64
