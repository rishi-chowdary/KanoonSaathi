import logging
import uuid

from app.extensions import db
from app.models.analysis import DocumentAnalysis
from app.models.document import Document
from app.models.key_info import ExtractedInformation
from app.nlp.extraction import PageData
from app.nlp.key_info import extract_contract_key_info
from app.nlp.summarizer import generate_extractive_summary

logger = logging.getLogger("lexilegal.services.analysis_service")


def process_key_info_and_summaries(
    doc: Document,
    full_text: str,
    pages: list[PageData] | None = None,
) -> tuple[DocumentAnalysis, ExtractedInformation]:
    """Extract key facts, dates, deadlines, and extractive summaries for a document."""
    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        # Should normally be created during clause processing
        analysis = DocumentAnalysis(
            id=str(uuid.uuid4()),
            document_id=doc.id,
            title=doc.original_filename.rsplit(".", 1)[0].replace("_", " ").title(),
            document_type="General Contract",
            purpose="",
            parties=[],
            summary_short="",
            summary_detailed="",
            main_conditions=[],
            obligations_summary=[],
            financial_terms_summary=[],
            llm_provider="local_nlp",
            llm_model="sbert_textrank_mmr",
            verification_rate=100.0,
        )
        db.session.add(analysis)

    summary_res = generate_extractive_summary(
        full_text=full_text,
        pages=pages,
        document_type=analysis.document_type or "General Contract",
        parties=analysis.parties or [],
    )

    analysis.summary_short = summary_res.summary_short
    analysis.summary_detailed = summary_res.summary_detailed
    analysis.purpose = summary_res.purpose
    analysis.main_conditions = summary_res.main_conditions
    analysis.obligations_summary = summary_res.obligations_summary
    analysis.financial_terms_summary = summary_res.financial_terms_summary

    key_info_res = extract_contract_key_info(full_text=full_text, pages=pages)

    key_info = ExtractedInformation.query.filter_by(analysis_id=analysis.id).first()
    if not key_info:
        key_info = ExtractedInformation(
            id=str(uuid.uuid4()),
            analysis_id=analysis.id,
        )
        db.session.add(key_info)

    key_info.contract_amount = key_info_res.contract_amount.value
    key_info.contract_amount_page = key_info_res.contract_amount.source_page
    key_info.payment_deadlines = key_info_res.payment_deadlines.value
    key_info.payment_deadlines_page = key_info_res.payment_deadlines.source_page
    key_info.penalties = key_info_res.penalties.value
    key_info.penalties_page = key_info_res.penalties.source_page
    key_info.start_date = key_info_res.start_date.value
    key_info.start_date_page = key_info_res.start_date.source_page
    key_info.end_date = key_info_res.end_date.value
    key_info.end_date_page = key_info_res.end_date.source_page
    key_info.renewal_date = key_info_res.renewal_date.value
    key_info.renewal_date_page = key_info_res.renewal_date.source_page
    key_info.notice_period = key_info_res.notice_period.value
    key_info.notice_period_page = key_info_res.notice_period.source_page
    key_info.termination_conditions = key_info_res.termination_conditions.value
    key_info.termination_conditions_page = (
        key_info_res.termination_conditions.source_page
    )
    key_info.obligations = [item["text"] for item in summary_res.obligations_summary]
    key_info.important_dates = key_info_res.important_dates

    db.session.commit()
    logger.info(
        "Extracted key info and generated extractive summaries for document %s.",
        doc.id,
    )
    return analysis, key_info


def get_document_detail_context(doc: Document) -> dict:
    """Load chunks, analysis, clauses, risks, key facts, and plain-language summary for a document."""
    from app.models.chunk import DocumentChunk
    from app.models.clause import ExtractedClause
    from app.models.missing_warning import MissingClauseWarning
    from app.models.risk import RiskFinding
    from app.nlp.readability import calculate_readability
    from app.nlp.simplification import simplify_simple_english

    chunks = (
        DocumentChunk.query.filter_by(document_id=doc.id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )
    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    clauses = []
    key_info = None
    risks = []
    missing_warnings = []
    if analysis:
        clauses = (
            ExtractedClause.query.filter_by(analysis_id=analysis.id)
            .order_by(
                ExtractedClause.source_page.asc(), ExtractedClause.created_at.asc()
            )
            .all()
        )
        key_info = ExtractedInformation.query.filter_by(analysis_id=analysis.id).first()
        risks = (
            RiskFinding.query.filter_by(analysis_id=analysis.id)
            .order_by(RiskFinding.source_page.asc(), RiskFinding.created_at.asc())
            .all()
        )
        missing_warnings = MissingClauseWarning.query.filter_by(
            analysis_id=analysis.id
        ).all()

    simplified_summary = None
    summary_readability = None
    if analysis and analysis.summary_short:
        simplified_summary = simplify_simple_english(analysis.summary_short)
        orig_metrics = calculate_readability(analysis.summary_short)
        simp_metrics = calculate_readability(simplified_summary)
        summary_readability = {
            "original_fre": orig_metrics["flesch_reading_ease"],
            "simplified_fre": simp_metrics["flesch_reading_ease"],
            "original_grade": orig_metrics["flesch_kincaid_grade"],
            "simplified_grade": simp_metrics["flesch_kincaid_grade"],
        }

    return {
        "document": doc,
        "chunks": chunks,
        "analysis": analysis,
        "clauses": clauses,
        "key_info": key_info,
        "risks": risks,
        "missing_warnings": missing_warnings,
        "simplified_summary": simplified_summary,
        "summary_readability": summary_readability,
    }
