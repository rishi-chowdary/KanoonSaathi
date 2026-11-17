from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class ExtractedClause(db.Model, TimestampMixin):
    """Extracted legal clause with classifications, 3-mode explanations, and evidence quote."""

    __tablename__ = "extracted_clauses"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    analysis_id = db.Column(
        db.String(36),
        db.ForeignKey("document_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    custom_label = db.Column(db.String(100), nullable=True)
    original_text = db.Column(db.Text, nullable=False)
    simplified_simple = db.Column(db.Text, nullable=False)
    simplified_detailed = db.Column(db.Text, nullable=False)
    simplified_professional = db.Column(db.Text, nullable=False)
    importance = db.Column(db.String(20), nullable=False, index=True)
    affected_party = db.Column(db.String(255), nullable=True)
    source_page = db.Column(db.Integer, nullable=False)
    section_reference = db.Column(db.String(100), nullable=True)
    evidence_quote = db.Column(db.Text, nullable=False)
    quote_verified = db.Column(db.Boolean, default=False, nullable=False)
    provenance = db.Column(db.String(30), default="EXTRACTED", nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "analysisId": self.analysis_id,
            "title": self.title,
            "category": self.category,
            "customLabel": self.custom_label,
            "originalText": self.original_text,
            "simplifiedSimple": self.simplified_simple,
            "simplifiedDetailed": self.simplified_detailed,
            "simplifiedProfessional": self.simplified_professional,
            "importance": self.importance,
            "affectedParty": self.affected_party,
            "sourcePage": self.source_page,
            "sectionReference": self.section_reference,
            "evidenceQuote": self.evidence_quote,
            "quoteVerified": self.quote_verified,
            "provenance": self.provenance,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<ExtractedClause {self.id} ({self.category} - {self.importance})>"
