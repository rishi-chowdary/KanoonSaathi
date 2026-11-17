from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import csrf
from app.models.analysis import DocumentAnalysis
from app.models.chunk import DocumentChunk
from app.models.clause import ExtractedClause
from app.models.key_info import ExtractedInformation
from app.models.missing_warning import MissingClauseWarning
from app.models.risk import RiskFinding
from app.services.document_service import (
    delete_document_for_user,
    get_document_for_user,
    list_documents_for_user,
    save_and_extract_document,
)

documents_bp = Blueprint("documents", __name__)


# -----------------------------------------------------------------------------
# Web Views (Jinja2 Templates)
# -----------------------------------------------------------------------------


@documents_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Upload document web view."""
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Please select a file to upload.", "danger")
            return render_template("documents/upload.html")

        file_bytes = file.read()
        try:
            doc, _extraction, clauses, _chunks = save_and_extract_document(
                user_id=current_user.id,
                file_bytes=file_bytes,
                filename=file.filename,
            )
            flash(
                f"Successfully extracted '{doc.original_filename}' ({doc.page_count} pages, {len(clauses)} clauses).",
                "success",
            )
            return redirect(url_for("documents.detail", doc_id=doc.id))
        except ValueError as err:
            flash(str(err), "danger")
            return render_template("documents/upload.html")

    return render_template("documents/upload.html")


@documents_bp.route("/documents")
@login_required
def list_view():
    """List of all user uploaded documents."""
    docs = list_documents_for_user(current_user.id)
    return render_template("documents/list.html", documents=docs)


@documents_bp.route("/documents/<doc_id>")
@login_required
def detail(doc_id: str):
    """Document overview, clause analysis, and extracted text inspector."""
    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        abort(404)

    # Fetch chunks ordered by chunk index
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

    return render_template(
        "documents/detail.html",
        document=doc,
        chunks=chunks,
        analysis=analysis,
        clauses=clauses,
        key_info=key_info,
        risks=risks,
        missing_warnings=missing_warnings,
    )


@documents_bp.route("/documents/<doc_id>/delete", methods=["POST"])
@login_required
def delete_view(doc_id: str):
    """Delete document from web UI."""
    success = delete_document_for_user(doc_id, current_user.id)
    if not success:
        abort(404)
    flash("Document deleted successfully.", "info")
    return redirect(url_for("documents.list_view"))


# -----------------------------------------------------------------------------
# REST API Endpoints (Grounded Backend & Test Clients)
# -----------------------------------------------------------------------------


@documents_bp.route("/api/documents/upload", methods=["POST"])
@csrf.exempt
def api_upload():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "No file provided in multipart upload"}), 400

    file_bytes = file.read()
    try:
        doc, _extraction, _clauses, _chunks = save_and_extract_document(
            user_id=current_user.id,
            file_bytes=file_bytes,
            filename=file.filename,
        )
        return jsonify(doc.to_dict()), 201
    except ValueError as err:
        return jsonify({"error": str(err)}), 400


@documents_bp.route("/api/documents", methods=["GET"])
@csrf.exempt
def api_list():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    docs = list_documents_for_user(current_user.id)
    return jsonify([d.to_dict() for d in docs]), 200


@documents_bp.route("/api/documents/<doc_id>", methods=["GET"])
@csrf.exempt
def api_get(doc_id: str):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    return jsonify(doc.to_dict()), 200


@documents_bp.route("/api/documents/<doc_id>/status", methods=["GET"])
@csrf.exempt
def api_status(doc_id: str):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    return (
        jsonify(
            {
                "id": doc.id,
                "status": doc.status,
                "pageCount": doc.page_count,
                "failureReason": doc.failure_reason,
            }
        ),
        200,
    )


@documents_bp.route("/api/documents/<doc_id>/text", methods=["GET"])
@csrf.exempt
def api_text(doc_id: str):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    chunks = (
        DocumentChunk.query.filter_by(document_id=doc.id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )

    # Group chunk contents by page number
    page_texts: dict[int, list[str]] = {}
    for c in chunks:
        page_texts.setdefault(c.page_number, []).append(c.content)

    pages_payload = [
        {"pageNumber": p_num, "text": "\n".join(texts)}
        for p_num, texts in sorted(page_texts.items())
    ]
    full_text = "\n\n".join(p["text"] for p in pages_payload)

    return (
        jsonify(
            {
                "documentId": doc.id,
                "pageCount": doc.page_count,
                "fullText": full_text,
                "pages": pages_payload,
            }
        ),
        200,
    )


@documents_bp.route("/api/documents/<doc_id>", methods=["DELETE"])
@csrf.exempt
def api_delete(doc_id: str):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    success = delete_document_for_user(doc_id, current_user.id)
    if not success:
        return jsonify({"error": "Document not found"}), 404

    return jsonify({"message": "Document deleted successfully"}), 200


@documents_bp.route("/api/documents/<doc_id>/clauses", methods=["GET"])
@csrf.exempt
def api_clauses(doc_id: str):
    """Retrieve extracted clauses with optional category, importance, and search filters."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        return (
            jsonify({"documentId": doc.id, "total": 0, "clauses": []}),
            200,
        )

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


@documents_bp.route("/api/documents/<doc_id>/analysis", methods=["GET"])
@csrf.exempt
def api_analysis(doc_id: str):
    """Retrieve full synthesized document analysis and clause summary."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        return jsonify({"error": "Analysis not ready"}), 404

    clauses = (
        ExtractedClause.query.filter_by(analysis_id=analysis.id)
        .order_by(ExtractedClause.source_page.asc())
        .all()
    )

    data = analysis.to_dict()
    data["clauses"] = [c.to_dict() for c in clauses]
    return jsonify(data), 200


@documents_bp.route("/api/documents/<doc_id>/key-info", methods=["GET"])
@csrf.exempt
def api_key_info(doc_id: str):
    """Retrieve structured commercial metadata and important dates with Rule 6 defaults."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        return jsonify({"error": "Analysis not ready"}), 404

    key_info = ExtractedInformation.query.filter_by(analysis_id=analysis.id).first()
    if not key_info:
        return jsonify({"error": "Key info not ready"}), 404

    return jsonify(key_info.to_dict()), 200


@documents_bp.route("/api/documents/<doc_id>/summary", methods=["GET"])
@csrf.exempt
def api_summary(doc_id: str):
    """Retrieve short and detailed extractive summaries and structured provisions."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        return jsonify({"error": "Analysis not ready"}), 404

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


@documents_bp.route("/api/documents/<doc_id>/risks", methods=["GET"])
@csrf.exempt
def api_risks(doc_id: str):
    """Retrieve grounded risk findings with exact page and quote evidence."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        return jsonify({"error": "Analysis not ready"}), 404

    risks = (
        RiskFinding.query.filter_by(analysis_id=analysis.id)
        .order_by(RiskFinding.source_page.asc(), RiskFinding.created_at.asc())
        .all()
    )
    return jsonify([r.to_dict() for r in risks]), 200


@documents_bp.route("/api/documents/<doc_id>/missing-provisions", methods=["GET"])
@csrf.exempt
def api_missing_provisions(doc_id: str):
    """Retrieve missing standard provisions labeled strictly as 'Possible omission'."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        return jsonify({"error": "Analysis not ready"}), 404

    warnings = MissingClauseWarning.query.filter_by(analysis_id=analysis.id).all()
    return jsonify([w.to_dict() for w in warnings]), 200


@documents_bp.route("/api/documents/<doc_id>/risk-distribution", methods=["GET"])
@csrf.exempt
def api_risk_distribution(doc_id: str):
    """Retrieve risk aggregation breakdown by level and category for Chart.js."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()
    if not analysis:
        return jsonify({"error": "Analysis not ready"}), 404

    from app.services.risk_service import get_risk_distribution

    distribution = get_risk_distribution(analysis.id)
    return jsonify(distribution), 200


# -----------------------------------------------------------------------------
# Interactive Chat & Extractive QA Endpoints
# -----------------------------------------------------------------------------


@documents_bp.route("/api/documents/<doc_id>/chat", methods=["POST"])
@csrf.exempt
def api_chat_send(doc_id: str):
    """Process incoming question about document and return extractive/grounded response."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    data = request.get_json(silent=True) or {}
    message = data.get("message") or data.get("question")
    if not message or not str(message).strip():
        return jsonify({"error": "question message must not be blank"}), 400

    from app.services.chat_service import send_chat_message

    conversation_id = data.get("conversationId")
    response_msg = send_chat_message(
        document_id=doc.id,
        user_id=current_user.id,
        message_text=str(message).strip(),
        conversation_id=conversation_id,
    )
    if not response_msg:
        return jsonify({"error": "Unable to process question"}), 400

    return jsonify(response_msg), 200


@documents_bp.route("/api/documents/<doc_id>/chat", methods=["GET"])
@documents_bp.route("/api/documents/<doc_id>/chat/conversations", methods=["GET"])
@csrf.exempt
def api_chat_conversations(doc_id: str):
    """Retrieve all conversations for a document owned by the user."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    from app.services.chat_service import get_conversations_for_document

    conversations = get_conversations_for_document(doc.id, current_user.id)
    return jsonify(conversations), 200


@documents_bp.route(
    "/api/documents/<doc_id>/chat/conversations/<conversation_id>/messages",
    methods=["GET"],
)
@csrf.exempt
def api_chat_messages(doc_id: str, conversation_id: str):
    """Retrieve message history for a conversation thread."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    from app.services.chat_service import get_conversation_messages

    messages = get_conversation_messages(doc.id, conversation_id, current_user.id)
    if messages is None:
        return jsonify({"error": "Conversation not found"}), 404

    return jsonify(messages), 200


@documents_bp.route(
    "/api/documents/<doc_id>/chat/conversations/<conversation_id>",
    methods=["DELETE"],
)
@csrf.exempt
def api_chat_delete_conversation(doc_id: str, conversation_id: str):
    """Delete a conversation thread."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    from app.services.chat_service import delete_conversation

    success = delete_conversation(doc.id, conversation_id, current_user.id)
    if not success:
        return jsonify({"error": "Conversation not found"}), 404

    return "", 204
