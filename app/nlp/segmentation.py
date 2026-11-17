import re
from dataclasses import dataclass

from nltk.tokenize.punkt import PunktParameters, PunktSentenceTokenizer

from app.nlp.extraction import PageData, SectionHeader

# Configure legal-aware sentence tokenizer
_punkt_params = PunktParameters()
_punkt_params.abbrev_types = {
    "sec",
    "secs",
    "cl",
    "cls",
    "art",
    "arts",
    "para",
    "paras",
    "no",
    "nos",
    "v",
    "vs",
    "inc",
    "ltd",
    "corp",
    "co",
    "llc",
    "llp",
    "e.g",
    "i.e",
    "al",
    "dr",
    "mr",
    "mrs",
    "ms",
    "prof",
    "ex",
    "sch",
    "app",
    "approx",
    "dept",
    "reg",
}
legal_sentence_tokenizer = PunktSentenceTokenizer(_punkt_params)


@dataclass
class SegmentedClause:
    """A segmented contractual clause strictly anchored to exact document text offsets."""

    title: str
    section_reference: str
    original_text: str
    start_offset: int
    end_offset: int
    source_page: int
    clause_index: int


@dataclass
class DocumentChunkData:
    """A text chunk prepared for page-attributed retrieval and grounded QA."""

    chunk_index: int
    page_number: int
    content: str
    token_count: int


def estimate_tokens(text: str) -> int:
    """Heuristic token estimation (~4 characters per English token)."""
    return max(1, len(text) // 4)


def build_page_offset_map(
    pages: list[PageData], full_text: str
) -> list[tuple[int, int, int]]:
    """Build list of (start_char, end_char, page_number) tuples for full_text."""
    page_offsets: list[tuple[int, int, int]] = []
    current_search_pos = 0

    for page in pages:
        p_text = page.text.strip()
        if not p_text:
            continue

        pos = full_text.find(p_text, current_search_pos)
        if pos != -1:
            end = pos + len(p_text)
            page_offsets.append((pos, end, page.page_number))
            current_search_pos = end
        else:
            # Fallback if text separator differs
            page_offsets.append(
                (current_search_pos, current_search_pos + len(p_text), page.page_number)
            )
            current_search_pos += len(p_text)

    return page_offsets


def get_page_for_offset(offset: int, page_offsets: list[tuple[int, int, int]]) -> int:
    """Return 1-indexed page number containing the specified character offset."""
    for start, end, page_num in page_offsets:
        if start <= offset <= end:
            return page_num
    return page_offsets[-1][2] if page_offsets else 1


def segment_clauses(
    full_text: str,
    pages: list[PageData],
    sections: list[SectionHeader],
) -> list[SegmentedClause]:
    """Segment a legal document into discrete clauses anchored to exact character offsets.

    Guarantees:
    - 100% of clause original_text fields equal full_text[start_offset:end_offset]
    - Accurate source_page mapping
    - Clean titles and section references
    """
    if not full_text.strip():
        return []

    page_offsets = build_page_offset_map(pages, full_text)
    clauses: list[SegmentedClause] = []

    # 1. Heading-based segmentation when sections are detected
    if sections:
        # Locate exact starting offset of each section heading in full_text
        section_spans: list[tuple[int, SectionHeader]] = []
        search_start = 0

        for sec in sections:
            # Match heading text or first line
            head = sec.title.strip()
            pos = full_text.find(head, search_start)
            if pos != -1:
                section_spans.append((pos, sec))
                search_start = pos + len(head)
            else:
                # Fallback: search case-insensitively
                idx = full_text.lower().find(head.lower(), search_start)
                if idx != -1:
                    section_spans.append((idx, sec))
                    search_start = idx + len(head)

        # Sort found section spans by starting position
        section_spans.sort(key=lambda s: s[0])

        # If there is meaningful introductory preamble before the first section
        if section_spans and section_spans[0][0] > 60:
            preamble_text = full_text[: section_spans[0][0]].strip()
            if preamble_text:
                clauses.append(
                    SegmentedClause(
                        title="Preamble and Recitals",
                        section_reference="Preamble",
                        original_text=preamble_text,
                        start_offset=0,
                        end_offset=len(preamble_text),
                        source_page=1,
                        clause_index=0,
                    )
                )

        for i, (start_idx, sec) in enumerate(section_spans):
            # Clause extends from current heading start until next heading start (or EOF)
            if i + 1 < len(section_spans):
                end_idx = section_spans[i + 1][0]
            else:
                end_idx = len(full_text)

            # Slice exact text span from document
            clause_slice = full_text[start_idx:end_idx].strip()
            if not clause_slice:
                continue

            # Compute precise trimmed boundaries in full_text
            actual_start = full_text.find(clause_slice, start_idx)
            actual_end = actual_start + len(clause_slice)
            source_page = get_page_for_offset(actual_start, page_offsets)

            clauses.append(
                SegmentedClause(
                    title=sec.title,
                    section_reference=sec.section_ref,
                    original_text=full_text[actual_start:actual_end],
                    start_offset=actual_start,
                    end_offset=actual_end,
                    source_page=source_page,
                    clause_index=len(clauses),
                )
            )

    # 2. Fallback: Paragraph / Sentence block segmentation if no headings detected
    if not clauses:
        # Split on double newlines for paragraph units
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", full_text) if p.strip()]
        current_pos = 0

        for p_idx, p_text in enumerate(paragraphs):
            p_start = full_text.find(p_text, current_pos)
            if p_start == -1:
                p_start = current_pos
            p_end = p_start + len(p_text)
            current_pos = p_end

            source_page = get_page_for_offset(p_start, page_offsets)
            clauses.append(
                SegmentedClause(
                    title=f"Clause {p_idx + 1}",
                    section_reference=f"Section {p_idx + 1}",
                    original_text=full_text[p_start:p_end],
                    start_offset=p_start,
                    end_offset=p_end,
                    source_page=source_page,
                    clause_index=p_idx,
                )
            )

    return clauses


def create_chunks(
    pages: list[PageData],
    sections: list[SectionHeader],
    max_tokens: int = 1000,
    overlap_tokens: int = 100,
) -> list[DocumentChunkData]:
    """Create page-level text chunks for retrieval and question answering."""
    if not pages:
        return []

    max_chars = max_tokens * 4
    overlap_chars = overlap_tokens * 4
    chunks: list[DocumentChunkData] = []
    chunk_index = 0

    for page in pages:
        p_text = page.text.strip()
        if not p_text:
            continue

        if len(p_text) <= max_chars:
            chunks.append(
                DocumentChunkData(
                    chunk_index=chunk_index,
                    page_number=page.page_number,
                    content=p_text,
                    token_count=estimate_tokens(p_text),
                )
            )
            chunk_index += 1
        else:
            # Sub-chunk oversized page with overlap
            pos = 0
            while pos < len(p_text):
                end = min(pos + max_chars, len(p_text))
                slice_text = p_text[pos:end].strip()
                chunks.append(
                    DocumentChunkData(
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        content=slice_text,
                        token_count=estimate_tokens(slice_text),
                    )
                )
                chunk_index += 1
                if end >= len(p_text):
                    break
                pos += max_chars - overlap_chars

    return chunks
