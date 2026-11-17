from flask import Blueprint, Response, abort
from flask_login import current_user, login_required

from app.blueprints.guards import require_owned_analysis
from app.extensions import csrf
from app.models.analysis import DocumentAnalysis
from app.services.document_service import get_document_for_user
from app.services.report_service import generate_pdf_report

reports_bp = Blueprint("reports", __name__)


def _pdf_response(doc_id: str, pdf_bytes: bytes) -> Response:
    safe_filename = f"lexilegal_report_{doc_id}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{safe_filename}"'},
    )


@reports_bp.route("/documents/<doc_id>/report", methods=["GET"])
@reports_bp.route("/documents/<doc_id>/report.pdf", methods=["GET"])
@login_required
def view_document_report(doc_id: str):
    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        abort(404)

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        abort(404)

    return _pdf_response(doc.id, generate_pdf_report(doc, analysis))


@reports_bp.route("/api/documents/<doc_id>/report", methods=["GET"])
@reports_bp.route("/api/documents/<doc_id>/report.pdf", methods=["GET"])
@csrf.exempt
def api_document_report(doc_id: str):
    doc, analysis, err = require_owned_analysis(doc_id)
    if err:
        return err
    return _pdf_response(doc.id, generate_pdf_report(doc, analysis))
