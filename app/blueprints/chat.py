from flask import Blueprint, jsonify, request
from flask_login import current_user

from app.blueprints.guards import require_owned_document
from app.extensions import csrf
from app.services.chat_service import (
    delete_conversation,
    get_conversation_messages,
    get_conversations_for_document,
    send_chat_message,
)

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/documents/<doc_id>/chat", methods=["POST"])
@csrf.exempt
def api_chat_send(doc_id: str):
    doc, err = require_owned_document(doc_id)
    if err:
        return err

    payload = request.get_json(silent=True) or {}
    message = payload.get("message") or payload.get("question")
    if not message or not str(message).strip():
        return jsonify({"error": "question message must not be blank"}), 400

    response_msg = send_chat_message(
        document_id=doc.id,
        user_id=current_user.id,
        message_text=str(message).strip(),
        conversation_id=payload.get("conversationId"),
    )
    if not response_msg:
        return jsonify({"error": "Unable to process question"}), 400
    return jsonify(response_msg), 200


@chat_bp.route("/api/documents/<doc_id>/chat", methods=["GET"])
@chat_bp.route("/api/documents/<doc_id>/chat/conversations", methods=["GET"])
@csrf.exempt
def api_chat_conversations(doc_id: str):
    doc, err = require_owned_document(doc_id)
    if err:
        return err
    return jsonify(get_conversations_for_document(doc.id, current_user.id)), 200


@chat_bp.route(
    "/api/documents/<doc_id>/chat/conversations/<conversation_id>/messages",
    methods=["GET"],
)
@csrf.exempt
def api_chat_messages(doc_id: str, conversation_id: str):
    doc, err = require_owned_document(doc_id)
    if err:
        return err

    messages = get_conversation_messages(doc.id, conversation_id, current_user.id)
    if messages is None:
        return jsonify({"error": "Conversation not found"}), 404
    return jsonify(messages), 200


@chat_bp.route(
    "/api/documents/<doc_id>/chat/conversations/<conversation_id>",
    methods=["DELETE"],
)
@csrf.exempt
def api_chat_delete_conversation(doc_id: str, conversation_id: str):
    doc, err = require_owned_document(doc_id)
    if err:
        return err

    if not delete_conversation(doc.id, conversation_id, current_user.id):
        return jsonify({"error": "Conversation not found"}), 404
    return "", 204
