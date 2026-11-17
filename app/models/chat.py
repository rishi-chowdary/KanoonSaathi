from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class ChatConversation(db.Model, TimestampMixin):

    __tablename__ = "chat_conversations"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    document_id = db.Column(
        db.String(36),
        db.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = db.Column(db.String(255), default="General Inquiries", nullable=False)

    __table_args__ = (db.Index("idx_chat_conv_doc_user", "document_id", "user_id"),)

    messages = db.relationship(
        "ChatMessage",
        backref="conversation",
        lazy="dynamic",
        order_by="ChatMessage.created_at.asc()",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "documentId": self.document_id,
            "userId": self.user_id,
            "title": self.title,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<ChatConversation {self.id} ('{self.title}')>"


class ChatMessage(db.Model, TimestampMixin):

    __tablename__ = "chat_messages"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    conversation_id = db.Column(
        db.String(36),
        db.ForeignKey("chat_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    citations = db.Column(db.JSON, default=list, nullable=False)
    addressed_in_document = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "conversationId": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "citations": self.citations or [],
            "addressedInDocument": self.addressed_in_document,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<ChatMessage {self.id} ({self.role})>"
