from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class RiskFinding(db.Model, TimestampMixin):
    """Identified contractual risk finding, severity rating, and advisory details."""

    __tablename__ = "risk_findings"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    analysis_id = db.Column(
        db.String(36),
        db.ForeignKey("document_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = db.Column(db.String(50), nullable=False, index=True)
    level = db.Column(db.String(20), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    original_clause = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    why_it_matters = db.Column(db.Text, nullable=False)
    possible_consequences = db.Column(db.Text, nullable=False)
    suggested_questions = db.Column(db.JSON, default=list, nullable=False)
    source_page = db.Column(db.Integer, nullable=False)
    evidence_quote = db.Column(db.Text, nullable=False)
    quote_verified = db.Column(db.Boolean, default=False, nullable=False)
    jurisdiction_caveat = db.Column(db.Text, nullable=True)
    provenance = db.Column(db.String(30), default="AI_INTERPRETATION", nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "analysisId": self.analysis_id,
            "category": self.category,
            "level": self.level,
            "title": self.title,
            "originalClause": self.original_clause,
            "explanation": self.explanation,
            "whyItMatters": self.why_it_matters,
            "possibleConsequences": self.possible_consequences,
            "suggestedQuestions": self.suggested_questions or [],
            "sourcePage": self.source_page,
            "evidenceQuote": self.evidence_quote,
            "quoteVerified": self.quote_verified,
            "jurisdictionCaveat": self.jurisdiction_caveat,
            "provenance": self.provenance,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<RiskFinding {self.id} ({self.level} - {self.category})>"
