import uuid
from pathlib import Path

from flask import current_app

from app.extensions import db
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.nlp.extraction import (
    ExtractionResult,
    compute_sha256,
    extract_document,
    validate_file,
)
from app.nlp.segmentation import (
    DocumentChunkData,
    SegmentedClause,
    create_chunks,
    segment_clauses,
)


def save_and_extract_document(
    user_id: str,
    file_bytes: bytes,
    filename: str,
) -> tuple[Document, ExtractionResult, list[SegmentedClause], list[DocumentChunkData]]:
    """Ingest, validate, store, and segment an uploaded contract document.

    Raises:
        ValueError: If file is oversized, invalid format, corrupted, or duplicate.
    """
    if not file_bytes:
        raise ValueError("File is empty (0 bytes).")

    max_size = current_app.config.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
    if len(file_bytes) > max_size:
        raise ValueError("File exceeds maximum allowed size of 10MB.")

    # 1. Validate magic bytes and format
    file_type = validate_file(file_bytes, filename)
    file_hash = compute_sha256(file_bytes)

    # 2. Check for duplicate file uploaded by the same user
    existing = Document.query.filter_by(user_id=user_id, file_hash=file_hash).first()
    if existing:
        raise ValueError(
            f"You have already uploaded this identical document ('{existing.original_filename}')."
        )

    # 3. Securely persist raw file to user upload directory
    doc_id = str(uuid.uuid4())
    upload_root = Path(current_app.config.get("UPLOAD_FOLDER", "uploads"))
    user_dir = upload_root / user_id
    user_dir.mkdir(parents=True, exist_ok=True)

    # Safe sanitized filename
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ")
    storage_filename = f"{doc_id}_{safe_name}"
    storage_path = user_dir / storage_filename

    with open(storage_path, "wb") as f:
        f.write(file_bytes)

    # 4. Extract text per page, structural sections, and OCR if required
    try:
        extraction = extract_document(file_bytes, filename)
    except Exception as e:  # noqa: BLE001 - file cleanup on any extraction error
        # Clean up stored file if extraction fails
        if storage_path.exists():
            storage_path.unlink()
        raise ValueError(f"Document extraction failed: {e}")

    # 5. Create Document model in database
    doc = Document(
        id=doc_id,
        user_id=user_id,
        original_filename=filename,
        storage_path=str(storage_path),
        file_type=file_type,
        file_size=len(file_bytes),
        file_hash=file_hash,
        page_count=extraction.page_count,
        is_scanned=extraction.is_scanned,
        status="EXTRACTED",
    )
    db.session.add(doc)

    # 6. Create page-level chunks for retrieval and question answering
    chunks_data = create_chunks(extraction.pages, extraction.sections)
    for c in chunks_data:
        chunk_model = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            chunk_index=c.chunk_index,
            page_number=c.page_number,
            content=c.content,
            token_count=c.token_count,
        )
        db.session.add(chunk_model)

    # 7. Segment document into discrete clauses with exact source text character offsets
    clauses_data = segment_clauses(
        extraction.full_text, extraction.pages, extraction.sections
    )
    db.session.commit()

    # Automatically classify clauses, importance, key facts, and summaries
    try:
        from app.services.analysis_service import process_key_info_and_summaries
        from app.services.clause_service import process_document_clauses
        from app.services.risk_service import process_document_risks_and_missing

        analysis, extracted_clauses = process_document_clauses(
            doc, extraction.full_text, clauses_data
        )
        process_key_info_and_summaries(doc, extraction.full_text, extraction.pages)
        process_document_risks_and_missing(
            doc, analysis, extracted_clauses, extraction.full_text
        )

    except Exception as exc:  # noqa: BLE001 - non-blocking clause extraction failure
        current_app.logger.warning(
            "Automatic clause and analysis processing error: %s", exc
        )
        doc.status = "COMPLETED_WITH_WARNINGS"
        db.session.commit()

    return doc, extraction, clauses_data, chunks_data


def get_document_for_user(document_id: str, user_id: str) -> Document | None:
    """Retrieve document owned by the specified user (returns None if not found/unauthorized)."""
    return Document.query.filter_by(id=document_id, user_id=user_id).first()


def list_documents_for_user(user_id: str, limit: int = 50) -> list[Document]:
    """Return documents owned by user, sorted by upload date descending."""
    return (
        Document.query.filter_by(user_id=user_id)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .all()
    )


def delete_document_for_user(document_id: str, user_id: str) -> bool:
    """Delete document and all associated records and files for the specified user."""
    doc = get_document_for_user(document_id, user_id)
    if not doc:
        return False

    # Remove physical file
    file_path = Path(doc.storage_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass

    db.session.delete(doc)
    db.session.commit()
    return True
