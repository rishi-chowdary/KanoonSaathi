from pathlib import Path

from app.nlp.extraction import extract_document
from app.nlp.segmentation import (
    create_chunks,
    legal_sentence_tokenizer,
    segment_clauses,
)

SAMPLES_DIR = Path("samples/contracts")

SAMPLE_FILES = [
    "clean_nda.pdf",
    "rental_agreement.pdf",
    "employment_agreement.pdf",
    "one_sided_agreement.pdf",
    "service_agreement.docx",
    "promissory_note.txt",
]


def test_all_extracted_clauses_are_exact_slices():
    """Every extracted clause must match full_text[start_offset:end_offset]."""
    total_clauses = 0

    for filename in SAMPLE_FILES:
        file_bytes = (SAMPLES_DIR / filename).read_bytes()
        res = extract_document(file_bytes, filename)
        clauses = segment_clauses(res.full_text, res.pages, res.sections)

        assert (
            len(clauses) >= 3
        ), f"{filename} produced too few clauses ({len(clauses)})"

        for c in clauses:
            total_clauses += 1
            # Verify slice equals original text character for character
            exact_slice = res.full_text[c.start_offset : c.end_offset]
            assert (
                exact_slice == c.original_text
            ), f"Offset mismatch in {filename} ({c.title}): slice '{exact_slice}' != orig '{c.original_text}'"

            # Verify offsets and page numbering validity
            assert 0 <= c.start_offset < c.end_offset <= len(res.full_text)
            assert 1 <= c.source_page <= res.page_count
            assert c.title.strip() != ""
            assert c.section_reference.strip() != ""

    assert (
        total_clauses >= 35
    ), f"Expected at least 35 clauses across samples, got {total_clauses}"


def test_chunking_page_attribution_and_tokens():
    """Page-level chunks preserve page number attribution and sensible token estimates."""
    file_bytes = (SAMPLES_DIR / "rental_agreement.pdf").read_bytes()
    res = extract_document(file_bytes, "rental_agreement.pdf")
    chunks = create_chunks(res.pages, res.sections)

    assert len(chunks) >= 2
    for c in chunks:
        assert 1 <= c.page_number <= res.page_count
        assert len(c.content.strip()) > 20
        assert c.token_count > 5


def test_legal_sentence_tokenizer_abbreviations():
    """Punkt tokenizer does not split across common legal abbreviations."""
    text = (
        "Under Sec. 1.2, Tenant shall notify Landlord, Inc. in accordance with Para. 4."
    )
    sentences = legal_sentence_tokenizer.tokenize(text)
    assert len(sentences) == 1
    assert "Sec. 1.2" in sentences[0]
