import hashlib
import io
import re
from dataclasses import dataclass, field

import docx
import pymupdf as fitz
import pytesseract
from PIL import Image


@dataclass
class PageData:
    """Extracted text and metadata for a single document page."""

    page_number: int
    text: str
    ocr_used: bool = False


@dataclass
class SectionHeader:
    """Detected section or clause header within a page."""

    title: str
    section_ref: str
    page_number: int


@dataclass
class ExtractionResult:
    """Full extraction bundle including page text, detected sections, and flags."""

    pages: list[PageData]
    sections: list[SectionHeader] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    full_text: str = ""
    page_count: int = 0
    is_scanned: bool = False


SECTION_PATTERNS = [
    re.compile(
        r"^(?:article|section|clause)\s+([0-9ivxlcdm]+|[a-z])(?:\.|\:|\s|\-)+\s*(.*)$",
        re.IGNORECASE,
    ),
    re.compile(r"^(\d+(?:\.\d+)*)\.?\s+([A-Z].*)$"),
    re.compile(
        r"^(?:schedule|exhibit|appendix)\s+([a-z0-9]+)(?:\.|\:|\s|\-)*\s*(.*)$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(recitals|definitions|governing law|termination|confidentiality|"
        r"indemnification|representations and warranties|severability|"
        r"entire agreement|dispute resolution|notices|force majeure|miscellaneous)\s*$",
        re.IGNORECASE,
    ),
]


def compute_sha256(file_bytes: bytes) -> str:
    """Calculate hex-encoded SHA-256 digest of binary content."""
    return hashlib.sha256(file_bytes).hexdigest()


def detect_sections(text: str, page_number: int) -> list[SectionHeader]:
    """Identify structural legal section titles within plain text lines."""
    sections: list[SectionHeader] = []
    lines = text.split("\n")
    for line in lines:
        cleaned = line.strip()
        if not cleaned or len(cleaned) > 120:
            continue

        for pattern in SECTION_PATTERNS:
            match = pattern.match(cleaned)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    ref = (
                        f"Section {groups[0]}"
                        if groups[0].replace(".", "").isdigit()
                        else groups[0]
                    )
                    title = cleaned
                elif len(groups) == 1:
                    ref = groups[0].title()
                    title = cleaned
                else:
                    ref = cleaned[:30]
                    title = cleaned

                sections.append(
                    SectionHeader(
                        title=title,
                        section_ref=ref,
                        page_number=page_number,
                    )
                )
                break
    return sections


def validate_file(file_bytes: bytes, filename: str) -> str:
    """Validate magic bytes, non-emptiness, and return standard format string."""
    if not file_bytes:
        raise ValueError("File is empty (0 bytes).")

    if len(file_bytes) > 10 * 1024 * 1024:
        raise ValueError("File exceeds maximum allowed size of 10MB.")

    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        if not file_bytes.startswith(b"%PDF"):
            raise ValueError("Corrupted PDF file: Missing '%PDF' magic header.")
        return "PDF"
    elif lower_name.endswith(".docx"):
        if not file_bytes.startswith(b"PK\x03\x04"):
            raise ValueError("Corrupted DOCX file: Missing 'PK' zip header.")
        return "DOCX"
    elif lower_name.endswith(".txt"):
        return "TXT"
    else:
        # Check by magic bytes if extension is missing/generic
        if file_bytes.startswith(b"%PDF"):
            return "PDF"
        elif file_bytes.startswith(b"PK\x03\x04"):
            return "DOCX"
        else:
            try:
                file_bytes.decode("utf-8")
                return "TXT"
            except UnicodeDecodeError:
                raise ValueError(
                    "Unsupported file format. Please upload PDF, DOCX, or TXT."
                )


def extract_pdf(file_bytes: bytes) -> ExtractionResult:
    """Extract text from PDF pages with automated Tesseract OCR fallback for scanned pages."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:  # noqa: BLE001 - catch C-level PyMuPDF stream errors
        raise ValueError(f"Unable to parse PDF document: {e}")

    if doc.is_encrypted or getattr(doc, "needs_pass", 0) > 0:
        doc.close()
        raise ValueError("Password-protected PDF documents are not supported.")

    if len(doc) == 0:
        doc.close()
        raise ValueError("PDF document has zero pages.")

    pages: list[PageData] = []
    sections: list[SectionHeader] = []
    warnings: list[str] = []
    is_scanned = False

    for idx in range(len(doc)):
        page = doc[idx]
        page_num = idx + 1
        page_text = page.get_text("text", clip=fitz.INFINITE_RECT()) or ""
        ocr_used = False

        # If native text extraction yields sparse content, trigger OCR on the rasterized page
        if len(page_text.strip()) < 50:
            try:
                pixmap = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pixmap.tobytes("png")))
                ocr_text = pytesseract.image_to_string(img)
                if len(ocr_text.strip()) > len(page_text.strip()):
                    page_text = ocr_text
                    ocr_used = True
                    is_scanned = True
            except Exception as ocr_err:  # noqa: BLE001 - non-fatal OCR retry log
                warnings.append(f"Page {page_num}: OCR attempt failed ({ocr_err})")

        cleaned_text = page_text.strip()
        pages.append(
            PageData(page_number=page_num, text=cleaned_text, ocr_used=ocr_used)
        )
        sections.extend(detect_sections(cleaned_text, page_num))

    doc.close()

    # Assemble cleaned full text separated by page breaks
    full_text = "\n\n".join(p.text for p in pages if p.text)
    return ExtractionResult(
        pages=pages,
        sections=sections,
        warnings=warnings,
        full_text=full_text,
        page_count=len(pages),
        is_scanned=is_scanned,
    )


def extract_docx(file_bytes: bytes) -> ExtractionResult:
    """Extract paragraphs and structured tables from a Word DOCX file."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
    except Exception as e:  # noqa: BLE001 - python-docx packaging error
        raise ValueError(f"Unable to parse DOCX document: {e}")

    blocks: list[str] = []
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt:
            blocks.append(txt)

    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
            if row_text:
                blocks.append(row_text)

    full_text = "\n\n".join(blocks)
    if not full_text.strip():
        raise ValueError("DOCX document contains no readable text content.")

    # Approximate page partitioning (Word documents lack explicit physical page markers)
    pages: list[PageData] = []
    sections: list[SectionHeader] = []
    chars_per_page = 3000
    pos = 0
    page_num = 1

    while pos < len(full_text):
        chunk_text = full_text[pos : pos + chars_per_page].strip()
        pages.append(PageData(page_number=page_num, text=chunk_text, ocr_used=False))
        sections.extend(detect_sections(chunk_text, page_num))
        pos += chars_per_page
        page_num += 1

    return ExtractionResult(
        pages=pages,
        sections=sections,
        full_text=full_text,
        page_count=len(pages),
        is_scanned=False,
    )


def extract_txt(file_bytes: bytes) -> ExtractionResult:
    """Extract text from plain UTF-8 (or Latin-1 fallback) text files."""
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode("latin-1")
        except Exception as e:  # noqa: BLE001 - fallback decoding error
            raise ValueError(f"Unable to decode text file: {e}")

    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Text file is empty.")

    # Split by form feed (\x0c) if present, otherwise group by logical page size
    if "\x0c" in cleaned:
        raw_pages = cleaned.split("\x0c")
    else:
        chars_per_page = 3000
        raw_pages = [
            cleaned[i : i + chars_per_page]
            for i in range(0, len(cleaned), chars_per_page)
        ]

    pages: list[PageData] = []
    sections: list[SectionHeader] = []
    for idx, p_text in enumerate(raw_pages, start=1):
        p_clean = p_text.strip()
        if p_clean:
            pages.append(PageData(page_number=idx, text=p_clean, ocr_used=False))
            sections.extend(detect_sections(p_clean, idx))

    return ExtractionResult(
        pages=pages,
        sections=sections,
        full_text=cleaned,
        page_count=len(pages),
        is_scanned=False,
    )


def extract_document(file_bytes: bytes, filename: str) -> ExtractionResult:
    """Main ingestion entrypoint dispatching extraction based on file type."""
    file_type = validate_file(file_bytes, filename)
    if file_type == "PDF":
        return extract_pdf(file_bytes)
    elif file_type == "DOCX":
        return extract_docx(file_bytes)
    elif file_type == "TXT":
        return extract_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
