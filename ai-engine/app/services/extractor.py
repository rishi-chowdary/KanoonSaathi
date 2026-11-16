import io
import re
from PIL import Image
import fitz  # PyMuPDF
import docx
import pytesseract

from app.schemas.extraction import (
    PageExtraction,
    SectionExtraction,
    ExtractionResponse,
)
from app.services.chunker import create_chunks


class ExtractionException(Exception):
    def __init__(self, code: str, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.status_code = status_code


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


def detect_sections(text: str, page_number: int) -> list[SectionExtraction]:
    sections: list[SectionExtraction] = []
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
                    ref = f"Section {groups[0]}" if groups[0].replace(".", "").isdigit() else groups[0]
                    title = cleaned
                elif len(groups) == 1:
                    ref = groups[0].title()
                    title = cleaned
                else:
                    ref = cleaned[:30]
                    title = cleaned

                sections.append(
                    SectionExtraction(
                        title=title,
                        section_ref=ref,
                        page_number=page_number,
                    )
                )
                break
    return sections


def guess_language(text: str) -> str:
    common_english = {"the", "of", "and", "to", "in", "shall", "agreement", "party", "parties"}
    words = {w.lower() for w in re.findall(r"\b[A-Za-z]{2,}\b", text[:3000])}
    matches = len(words.intersection(common_english))
    return "en" if matches >= 2 else "unknown"


def extract_pdf(file_bytes: bytes) -> tuple[list[PageExtraction], list[SectionExtraction], list[str]]:
    if not file_bytes:
        raise ExtractionException("EMPTY_FILE", "file is empty", 400)

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ExtractionException("CORRUPTED_FILE", f"corrupted or invalid pdf: {e}", 400)

    if doc.is_encrypted:
        doc.close()
        raise ExtractionException("PASSWORD_PROTECTED", "pdf is password protected", 400)

    if len(doc) == 0:
        doc.close()
        raise ExtractionException("EMPTY_FILE", "pdf has no pages", 400)

    pages: list[PageExtraction] = []
    sections: list[SectionExtraction] = []
    warnings: list[str] = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1
        page_text = page.get_text() or ""
        ocr_used = False

        # If page has very little extracted text, attempt OCR via Tesseract
        if len(page_text.strip()) < 50:
            try:
                pix = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_result = pytesseract.image_to_string(img)
                if len(ocr_result.strip()) > len(page_text.strip()):
                    page_text = ocr_result
                    ocr_used = True
            except Exception as ocr_err:
                warnings.append(f"page {page_num}: ocr failed or tesseract unavailable ({ocr_err})")

        page_sections = detect_sections(page_text, page_num)
        sections.extend(page_sections)

        pages.append(
            PageExtraction(
                page_number=page_num,
                text=page_text.strip(),
                ocr_used=ocr_used,
            )
        )

    doc.close()
    return pages, sections, warnings


def extract_docx(file_bytes: bytes) -> tuple[list[PageExtraction], list[SectionExtraction], list[str]]:
    if not file_bytes:
        raise ExtractionException("EMPTY_FILE", "file is empty", 400)

    try:
        doc = docx.Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise ExtractionException("CORRUPTED_FILE", f"corrupted or invalid docx: {e}", 400)

    paragraphs_and_tables: list[str] = []
    for p in doc.paragraphs:
        if p.text.strip():
            paragraphs_and_tables.append(p.text.strip())

    for t in doc.tables:
        table_rows = []
        for row in t.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                table_rows.append(row_text)
        if table_rows:
            paragraphs_and_tables.append("\n".join(table_rows))

    if not paragraphs_and_tables:
        raise ExtractionException("EMPTY_FILE", "docx contains no text content", 400)

    # DOCX lacks native pagination: split text into virtual pages (~3000 chars)
    full_text = "\n\n".join(paragraphs_and_tables)
    pages: list[PageExtraction] = []
    sections: list[SectionExtraction] = []
    warnings: list[str] = [
        "DOCX format lacks native pagination; page numbers are approximated using character count heuristics."
    ]

    target_page_size = 3000
    paragraphs = full_text.split("\n\n")
    current_page_text: list[str] = []
    current_page_len = 0
    page_number = 1

    for p in paragraphs:
        if current_page_len + len(p) > target_page_size and current_page_text:
            text_str = "\n\n".join(current_page_text)
            pages.append(PageExtraction(page_number=page_number, text=text_str, ocr_used=False))
            sections.extend(detect_sections(text_str, page_number))
            page_number += 1
            current_page_text = [p]
            current_page_len = len(p)
        else:
            current_page_text.append(p)
            current_page_len += len(p)

    if current_page_text:
        text_str = "\n\n".join(current_page_text)
        pages.append(PageExtraction(page_number=page_number, text=text_str, ocr_used=False))
        sections.extend(detect_sections(text_str, page_number))

    return pages, sections, warnings


def extract_txt(file_bytes: bytes) -> tuple[list[PageExtraction], list[SectionExtraction], list[str]]:
    if not file_bytes:
        raise ExtractionException("EMPTY_FILE", "file is empty", 400)

    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode("latin-1")
        except Exception as e:
            raise ExtractionException("CORRUPTED_FILE", f"could not decode text file: {e}", 400)

    if not text.strip():
        raise ExtractionException("EMPTY_FILE", "text file contains no content", 400)

    target_page_size = 3000
    paragraphs = text.split("\n\n")
    pages: list[PageExtraction] = []
    sections: list[SectionExtraction] = []
    warnings: list[str] = []

    current_page_text: list[str] = []
    current_page_len = 0
    page_number = 1

    for p in paragraphs:
        if current_page_len + len(p) > target_page_size and current_page_text:
            text_str = "\n\n".join(current_page_text)
            pages.append(PageExtraction(page_number=page_number, text=text_str, ocr_used=False))
            sections.extend(detect_sections(text_str, page_number))
            page_number += 1
            current_page_text = [p]
            current_page_len = len(p)
        else:
            current_page_text.append(p)
            current_page_len += len(p)

    if current_page_text:
        text_str = "\n\n".join(current_page_text)
        pages.append(PageExtraction(page_number=page_number, text=text_str, ocr_used=False))
        sections.extend(detect_sections(text_str, page_number))

    return pages, sections, warnings


def process_document(filename: str, file_bytes: bytes) -> ExtractionResponse:
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        pages, sections, warnings = extract_pdf(file_bytes)
    elif lower_name.endswith(".docx"):
        pages, sections, warnings = extract_docx(file_bytes)
    elif lower_name.endswith(".txt"):
        pages, sections, warnings = extract_txt(file_bytes)
    else:
        raise ExtractionException(
            "UNSUPPORTED_TYPE",
            f"unsupported file format for '{filename}'; only PDF, DOCX, and TXT are supported",
            400,
        )

    all_text = " ".join(p.text for p in pages)
    lang = guess_language(all_text)
    chunks = create_chunks(pages, sections)

    return ExtractionResponse(
        pages=pages,
        sections=sections,
        chunks=chunks,
        language_guess=lang,
        warnings=warnings,
    )
