from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class Document(db.Model, TimestampMixin):
    """Uploaded contract document metadata and processing state."""

    __tablename__ = "documents"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    page_count = db.Column(db.Integer, default=0, nullable=False)
    is_scanned = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(50), default="UPLOADED", nullable=False, index=True)
    failure_reason = db.Column(db.Text, nullable=True)

    __table_args__ = (db.Index("idx_documents_user_hash", "user_id", "file_hash"),)

    analysis = db.relationship(
        "DocumentAnalysis",
        backref="document",
        uselist=False,
        cascade="all, delete-orphan",
    )
    chunks = db.relationship(
        "DocumentChunk",
        backref="document",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    conversations = db.relationship(
        "ChatConversation",
        backref="document",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "userId": self.user_id,
            "originalFilename": self.original_filename,
            "fileType": self.file_type,
            "fileSize": self.file_size,
            "pageCount": self.page_count,
            "isScanned": self.is_scanned,
            "status": self.status,
            "failureReason": self.failure_reason,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Document {self.id} {self.original_filename} ({self.status})>"
