from flask import Blueprint, jsonify, request

from app.blueprints.guards import require_owned_analysis, require_owned_document
from app.extensions import csrf
from app.models.analysis import DocumentAnalysis
from app.models.clause import ExtractedClause
from app.models.key_info import ExtractedInformation
from app.models.missing_warning import MissingClauseWarning
from app.models.risk import RiskFinding
from app.services.risk_service import get_risk_distribution

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/api/documents/<doc_id>/clauses", methods=["GET"])
@csrf.exempt
def api_clauses(doc_id: str):
    doc, err = require_owned_document(doc_id)
    if err:
        return err

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        return jsonify({"documentId": doc.id, "total": 0, "clauses": []}), 200

    query = ExtractedClause.query.filter_by(analysis_id=analysis.id)

    cat_filter = request.args.get("category")
    if cat_filter:
        query = query.filter(ExtractedClause.category.ilike(cat_filter))

    imp_filter = request.args.get("importance")
    if imp_filter:
        query = query.filter(ExtractedClause.importance == imp_filter.upper())

    search_query = request.args.get("search")
    if search_query:
        term = f"%{search_query}%"
        query = query.filter(
            (ExtractedClause.title.ilike(term))
            | (ExtractedClause.original_text.ilike(term))
            | (ExtractedClause.evidence_quote.ilike(term))
        )

    clauses = query.order_by(
        ExtractedClause.source_page.asc(), ExtractedClause.created_at.asc()
    ).all()

    return (
        jsonify(
            {
                "documentId": doc.id,
                "analysisId": analysis.id,
                "documentType": analysis.document_type,
                "total": len(clauses),
                "clauses": [c.to_dict() for c in clauses],
            }
        ),
        200,
    )


@analysis_bp.route("/api/documents/<doc_id>/analysis", methods=["GET"])
@csrf.exempt
def api_analysis(doc_id: str):
    _doc, analysis, err = require_owned_analysis(doc_id)
    if err:
        return err

    clauses = (
        ExtractedClause.query.filter_by(analysis_id=analysis.id)
        .order_by(ExtractedClause.source_page.asc())
        .all()
    )
    analysis_payload = analysis.to_dict()
    analysis_payload["clauses"] = [c.to_dict() for c in clauses]
    return jsonify(analysis_payload), 200


@analysis_bp.route("/api/documents/<doc_id>/key-info", methods=["GET"])
@csrf.exempt
def api_key_info(doc_id: str):
    _doc, analysis, err = require_owned_analysis(doc_id)
    if err:
        return err

    key_info = ExtractedInformation.query.filter_by(analysis_id=analysis.id).first()
    if not key_info:
        return jsonify({"error": "Key info not ready"}), 404
    return jsonify(key_info.to_dict()), 200


@analysis_bp.route("/api/documents/<doc_id>/summary", methods=["GET"])
@csrf.exempt
def api_summary(doc_id: str):
    doc, analysis, err = require_owned_analysis(doc_id)
    if err:
        return err

    return (
        jsonify(
            {
                "documentId": doc.id,
                "documentType": analysis.document_type,
                "shortSummary": analysis.summary_short,
                "detailedSummary": analysis.summary_detailed,
                "purpose": analysis.purpose,
                "mainConditions": analysis.main_conditions or [],
                "obligationsSummary": analysis.obligations_summary or [],
                "financialTermsSummary": analysis.financial_terms_summary or [],
            }
        ),
        200,
    )


@analysis_bp.route("/api/documents/<doc_id>/risks", methods=["GET"])
@csrf.exempt
def api_risks(doc_id: str):
    _doc, analysis, err = require_owned_analysis(doc_id)
    if err:
        return err

    risks = (
        RiskFinding.query.filter_by(analysis_id=analysis.id)
        .order_by(RiskFinding.source_page.asc(), RiskFinding.created_at.asc())
        .all()
    )
    return jsonify([r.to_dict() for r in risks]), 200


@analysis_bp.route("/api/documents/<doc_id>/missing-provisions", methods=["GET"])
@csrf.exempt
def api_missing_provisions(doc_id: str):
    _doc, analysis, err = require_owned_analysis(doc_id)
    if err:
        return err

    warnings = MissingClauseWarning.query.filter_by(analysis_id=analysis.id).all()
    return jsonify([w.to_dict() for w in warnings]), 200


@analysis_bp.route("/api/documents/<doc_id>/risk-distribution", methods=["GET"])
@csrf.exempt
def api_risk_distribution(doc_id: str):
    _doc, analysis, err = require_owned_analysis(doc_id)
    if err:
        return err

    return jsonify(get_risk_distribution(analysis.id)), 200
