from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class MissingClauseWarning(db.Model, TimestampMixin):

    __tablename__ = "missing_clause_warnings"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    analysis_id = db.Column(
        db.String(36),
        db.ForeignKey("document_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = db.Column(db.String(100), nullable=False)
    clause_name = db.Column(db.String(255), nullable=False)
    why_it_matters = db.Column(db.Text, nullable=False)
    typical_provision = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    label = db.Column(db.String(50), default="Possible omission", nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "analysisId": self.analysis_id,
            "category": self.category,
            "clauseName": self.clause_name,
            "whyItMatters": self.why_it_matters,
            "typicalProvision": self.typical_provision,
            "riskLevel": self.risk_level,
            "label": self.label,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<MissingClauseWarning {self.clause_name} ({self.risk_level})>"
