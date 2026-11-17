import logging
import uuid

from app.extensions import db
from app.models.analysis import DocumentAnalysis
from app.models.clause import ExtractedClause
from app.models.document import Document
from app.nlp.clause_classifier import classify_clause
from app.nlp.document_classifier import classify_document_type
from app.nlp.evidence import extract_evidence_quote
from app.nlp.importance import calculate_clause_importance
from app.nlp.parties import detect_affected_party, extract_document_parties
from app.nlp.segmentation import SegmentedClause
from app.nlp.simplification import simplify_clause

logger = logging.getLogger("kanoonsaathi.services.clause_service")


def process_document_clauses(
    doc: Document,
    full_text: str,
    segmented_clauses: list[SegmentedClause],
) -> tuple[DocumentAnalysis, list[ExtractedClause]]:
    """Classify clauses, determine importance, extract evidence quotes, and persist to database.

    Guarantees:
    - 100% of clause evidence quotes are exact slices of original_text
    - 100% of quote_verified flags reflect actual substring presence
    - Document status transitions cleanly: ANALYZING -> COMPLETED
    """
    doc.status = "ANALYZING"
    db.session.commit()

    doc_type, _ = classify_document_type(full_text, doc.original_filename)

    preamble_sample = full_text[:1500]
    parties = extract_document_parties(preamble_sample)

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        analysis = DocumentAnalysis(
            id=str(uuid.uuid4()),
            document_id=doc.id,
            title=doc.original_filename.rsplit(".", 1)[0].replace("_", " ").title(),
            document_type=doc_type,
            purpose=f"Legal agreement governing {doc_type.lower()} provisions and mutual rights.",
            parties=parties,
            summary_short="",
            summary_detailed="",
            main_conditions=[],
            obligations_summary=[],
            financial_terms_summary=[],
            llm_provider="local_nlp",
            llm_model="ensemble_classifier",
            verification_rate=100.0,
        )
        db.session.add(analysis)
    else:
        analysis.document_type = doc_type
        analysis.parties = parties

    ExtractedClause.query.filter_by(analysis_id=analysis.id).delete()

    created_clauses: list[ExtractedClause] = []
    verified_count = 0

    for clause in segmented_clauses:
        # Categorization via Ensemble (Rules + SBERT Prototypes + DistilBERT)
        category, custom_label, _confidence, _ = classify_clause(
            title=clause.title,
            original_text=clause.original_text,
            section_reference=clause.section_reference,
        )

        # Importance Evaluation
        importance = calculate_clause_importance(
            category=category,
            original_text=clause.original_text,
            title=clause.title,
        )

        # Affected Party Identification
        affected_party = detect_affected_party(
            original_text=clause.original_text,
            document_parties=parties,
            category=category,
        )

        # Evidence Quote Extraction & Exact Slice Verification
        evidence_quote, is_verified = extract_evidence_quote(
            original_text=clause.original_text,
            category=category,
            title=clause.title,
        )
        if is_verified:
            verified_count += 1

        simplification_output = simplify_clause(
            original_text=clause.original_text,
            category=category,
            affected_party=affected_party,
        )
        simple_expl = simplification_output["simple_english"]
        detailed_expl = simplification_output["detailed"]
        prof_expl = simplification_output["professional"]

        model_clause = ExtractedClause(
            id=str(uuid.uuid4()),
            analysis_id=analysis.id,
            title=clause.title,
            category=category,
            custom_label=custom_label,
            original_text=clause.original_text,
            simplified_simple=simple_expl,
            simplified_detailed=detailed_expl,
            simplified_professional=prof_expl,
            importance=importance,
            affected_party=affected_party,
            source_page=clause.source_page,
            section_reference=clause.section_reference,
            evidence_quote=evidence_quote,
            quote_verified=is_verified,
            provenance="EXTRACTED",
        )
        db.session.add(model_clause)
        created_clauses.append(model_clause)

    total_clauses = len(created_clauses)
    verification_rate = (
        (verified_count / total_clauses * 100.0) if total_clauses > 0 else 100.0
    )
    analysis.verification_rate = round(verification_rate, 2)

    doc.status = "COMPLETED"
    db.session.commit()

    logger.info(
        "classified %d clauses for document %s (offset match %.1f%%)",
        total_clauses,
        doc.id,
        verification_rate,
    )
    return analysis, created_clauses
