from flask import jsonify
from flask_login import current_user

from app.models.analysis import DocumentAnalysis
from app.services.document_service import get_document_for_user


def require_owned_document(doc_id: str):
    """Verify session auth and document ownership for API routes.

    Returns (doc, None) on success or (None, error_response_tuple) on failure.
    """
    if not current_user.is_authenticated:
        return None, (jsonify({"error": "Unauthorized"}), 401)
    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return None, (jsonify({"error": "Document not found"}), 404)
    return doc, None


def require_owned_analysis(doc_id: str):
    """Verify auth, ownership, and existing analysis record for API routes."""
    doc, err = require_owned_document(doc_id)
    if err:
        return None, None, err
    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        return doc, None, (jsonify({"error": "Analysis not ready"}), 404)
    return doc, analysis, None
