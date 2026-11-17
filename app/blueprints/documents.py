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

from app.blueprints.guards import require_owned_document
from app.extensions import csrf
from app.models.chunk import DocumentChunk
from app.services.analysis_service import get_document_detail_context
from app.services.document_service import (
    delete_document_for_user,
    get_document_for_user,
    list_documents_for_user,
    save_and_extract_document,
)

documents_bp = Blueprint("documents", __name__)


@documents_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Please select a file to upload.", "danger")
            return render_template("documents/upload.html")

        try:
            doc, _extraction, clauses, _chunks = save_and_extract_document(
                user_id=current_user.id,
                file_bytes=file.read(),
                filename=file.filename,
            )
            flash(
                f"Extracted '{doc.original_filename}' ({doc.page_count} pages, {len(clauses)} clauses).",
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
    docs = list_documents_for_user(current_user.id)
    return render_template("documents/list.html", documents=docs)


@documents_bp.route("/documents/<doc_id>")
@login_required
def detail(doc_id: str):
    doc = get_document_for_user(doc_id, current_user.id)
    if not doc:
        abort(404)
    context = get_document_detail_context(doc)
    return render_template("documents/detail.html", **context)


@documents_bp.route("/documents/<doc_id>/delete", methods=["POST"])
@login_required
def delete_view(doc_id: str):
    if not delete_document_for_user(doc_id, current_user.id):
        abort(404)
    flash("Document deleted.", "info")
    return redirect(url_for("documents.list_view"))


@documents_bp.route("/api/documents/upload", methods=["POST"])
@csrf.exempt
def api_upload():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "No file provided in multipart upload"}), 400

    try:
        doc, _extraction, _clauses, _chunks = save_and_extract_document(
            user_id=current_user.id,
            file_bytes=file.read(),
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
    doc, err = require_owned_document(doc_id)
    if err:
        return err
    return jsonify(doc.to_dict()), 200


@documents_bp.route("/api/documents/<doc_id>/status", methods=["GET"])
@csrf.exempt
def api_status(doc_id: str):
    doc, err = require_owned_document(doc_id)
    if err:
        return err
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
    doc, err = require_owned_document(doc_id)
    if err:
        return err

    chunks = (
        DocumentChunk.query.filter_by(document_id=doc.id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )
    page_texts: dict[int, list[str]] = {}
    for chunk in chunks:
        page_texts.setdefault(chunk.page_number, []).append(chunk.content)

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
    if not delete_document_for_user(doc_id, current_user.id):
        return jsonify({"error": "Document not found"}), 404
    return jsonify({"message": "Document deleted successfully"}), 200
