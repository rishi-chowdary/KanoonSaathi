"""LexiLegal AI — Chat Service.

Orchestrates multi-turn grounded contract conversations, page-aware passage retrieval,
factual routing, and extractive QA with strict tenant isolation.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from app.extensions import db
from app.models.analysis import DocumentAnalysis
from app.models.chat import ChatConversation, ChatMessage
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.nlp.qa_engine import answer_document_query

logger = logging.getLogger("lexilegal.chat_service")


def get_conversations_for_document(
    document_id: str, user_id: str
) -> list[dict[str, Any]]:
    """Return all chat conversations for a document owned by user_id."""
    doc = Document.query.filter_by(id=document_id, user_id=user_id).first()
    if not doc:
        return []

    conversations = (
        ChatConversation.query.filter_by(document_id=document_id, user_id=user_id)
        .order_by(ChatConversation.updated_at.desc())
        .all()
    )

    results = []
    for conv in conversations:
        msg_count = conv.messages.count()
        last_msg = conv.messages.order_by(ChatMessage.created_at.desc()).first()
        results.append(
            {
                "id": conv.id,
                "documentId": conv.document_id,
                "title": conv.title,
                "createdAt": conv.created_at.isoformat() if conv.created_at else None,
                "updatedAt": conv.updated_at.isoformat() if conv.updated_at else None,
                "messageCount": msg_count,
                "lastMessage": last_msg.to_dict() if last_msg else None,
            }
        )
    return results


def get_conversation_messages(
    document_id: str,
    conversation_id: str,
    user_id: str,
) -> list[dict[str, Any]] | None:
    """Return chronological message history for a conversation if authorized."""
    conv = ChatConversation.query.filter_by(
        id=conversation_id, document_id=document_id, user_id=user_id
    ).first()
    if not conv:
        return None

    messages = conv.messages.order_by(ChatMessage.created_at.asc()).all()
    return [m.to_dict() for m in messages]


def delete_conversation(
    document_id: str,
    conversation_id: str,
    user_id: str,
) -> bool:
    """Delete a conversation thread and its associated messages."""
    conv = ChatConversation.query.filter_by(
        id=conversation_id, document_id=document_id, user_id=user_id
    ).first()
    if not conv:
        return False

    db.session.delete(conv)
    db.session.commit()
    return True


def send_chat_message(
    document_id: str,
    user_id: str,
    message_text: str,
    conversation_id: str | None = None,
) -> dict[str, Any] | None:
    """Process incoming user question: retrieve context, execute QA, and persist turn."""
    clean_msg = (message_text or "").strip()
    if not clean_msg:
        return None

    # Enforce strict document ownership
    doc = Document.query.filter_by(id=document_id, user_id=user_id).first()
    if not doc:
        return None

    # Get or create conversation thread
    if conversation_id:
        conv = ChatConversation.query.filter_by(
            id=conversation_id, document_id=document_id, user_id=user_id
        ).first()
        if not conv:
            return None
    else:
        conv_title = clean_msg if len(clean_msg) <= 60 else clean_msg[:57] + "..."
        conv = ChatConversation(
            id=str(uuid.uuid4()),
            document_id=doc.id,
            user_id=user_id,
            title=conv_title,
        )
        db.session.add(conv)
        db.session.flush()

    user_msg = ChatMessage(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="user",
        content=clean_msg,
        citations=[],
        addressed_in_document=True,
    )
    db.session.add(user_msg)

    chunks = (
        DocumentChunk.query.filter_by(document_id=doc.id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )
    analysis = DocumentAnalysis.query.filter_by(document_id=doc.id).first()

    qa_result = answer_document_query(clean_msg, analysis, chunks)

    asst_msg = ChatMessage(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="assistant",
        content=qa_result.get(
            "answer", "The document does not appear to address this."
        ),
        citations=qa_result.get("citations", []),
        addressed_in_document=qa_result.get("addressedInDocument", False),
    )
    db.session.add(asst_msg)

    conv.updated_at = datetime.now(UTC)
    db.session.commit()

    return asst_msg.to_dict()
