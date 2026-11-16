from app.schemas.extraction import PageExtraction, SectionExtraction, ChunkExtraction


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def create_chunks(
    pages: list[PageExtraction],
    sections: list[SectionExtraction],
    max_tokens: int = 3500,
    overlap_tokens: int = 250,
) -> list[ChunkExtraction]:
    if not pages:
        return []

    max_chars = max_tokens * 4
    overlap_chars = overlap_tokens * 4

    # Build map of page_number -> section_ref
    page_sections: dict[int, str] = {}
    for s in sections:
        if s.page_number not in page_sections:
            page_sections[s.page_number] = s.section_ref

    chunks: list[ChunkExtraction] = []
    chunk_index = 0

    for page in pages:
        page_text = page.text.strip()
        if not page_text:
            continue

        sec_ref = page_sections.get(page.page_number)

        # If page fits in max_chars, create chunk for this page
        if len(page_text) <= max_chars:
            chunks.append(
                ChunkExtraction(
                    chunk_index=chunk_index,
                    page_start=page.page_number,
                    page_end=page.page_number,
                    section_ref=sec_ref,
                    content=page_text,
                    token_count=estimate_tokens(page_text),
                )
            )
            chunk_index += 1
        else:
            # Split oversized page into chunks with overlap
            pos = 0
            while pos < len(page_text):
                end = min(pos + max_chars, len(page_text))
                slice_text = page_text[pos:end].strip()
                chunks.append(
                    ChunkExtraction(
                        chunk_index=chunk_index,
                        page_start=page.page_number,
                        page_end=page.page_number,
                        section_ref=sec_ref,
                        content=slice_text,
                        token_count=estimate_tokens(slice_text),
                    )
                )
                chunk_index += 1
                if end >= len(page_text):
                    break
                pos += max_chars - overlap_chars

    return chunks
