from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class DocumentAnalysis(db.Model, TimestampMixin):

    __tablename__ = "document_analyses"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    document_id = db.Column(
        db.String(36),
        db.ForeignKey("documents.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    title = db.Column(db.String(255), nullable=True)
    document_type = db.Column(db.String(100), nullable=True)
    purpose = db.Column(db.Text, nullable=True)
    parties = db.Column(db.JSON, default=list, nullable=False)
    summary_short = db.Column(db.Text, nullable=False)
    summary_detailed = db.Column(db.Text, nullable=False)
    main_conditions = db.Column(db.JSON, default=list, nullable=False)
    obligations_summary = db.Column(db.JSON, default=list, nullable=False)
    financial_terms_summary = db.Column(db.JSON, default=list, nullable=False)
    llm_provider = db.Column(db.String(50), default="local_nlp", nullable=False)
    llm_model = db.Column(db.String(100), default="extractive_textrank", nullable=False)
    verification_rate = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)

    clauses = db.relationship(
        "ExtractedClause",
        backref="analysis",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    risks = db.relationship(
        "RiskFinding",
        backref="analysis",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    key_info = db.relationship(
        "ExtractedInformation",
        backref="analysis",
        uselist=False,
        cascade="all, delete-orphan",
    )
    missing_warnings = db.relationship(
        "MissingClauseWarning",
        backref="analysis",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "documentId": self.document_id,
            "title": self.title,
            "documentType": self.document_type,
            "purpose": self.purpose,
            "parties": self.parties or [],
            "shortSummary": self.summary_short,
            "detailedSummary": self.summary_detailed,
            "mainConditions": self.main_conditions or [],
            "obligationsSummary": self.obligations_summary or [],
            "financialTermsSummary": self.financial_terms_summary or [],
            "verificationRate": float(self.verification_rate or 0.0),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<DocumentAnalysis {self.id} for doc {self.document_id}>"
