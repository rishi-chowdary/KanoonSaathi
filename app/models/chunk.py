from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class DocumentChunk(db.Model, TimestampMixin):
    """Segmented contract text chunk for retrieval and page-level attribution."""

    __tablename__ = "document_chunks"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    document_id = db.Column(
        db.String(36),
        db.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = db.Column(db.Integer, nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    token_count = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (db.Index("idx_chunks_doc_chunk", "document_id", "chunk_index"),)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "documentId": self.document_id,
            "chunkIndex": self.chunk_index,
            "pageNumber": self.page_number,
            "content": self.content,
            "tokenCount": self.token_count,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<DocumentChunk {self.chunk_index} (page {self.page_number}) of doc {self.document_id}>"
