from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid


class ExtractedInformation(db.Model, TimestampMixin):
    """Structured contract metadata: amounts, critical dates, deadlines, and parties."""

    __tablename__ = "extracted_information"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    analysis_id = db.Column(
        db.String(36),
        db.ForeignKey("document_analyses.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    contract_amount = db.Column(db.String(255), default="Not specified", nullable=False)
    contract_amount_page = db.Column(db.Integer, nullable=True)
    payment_deadlines = db.Column(db.Text, default="Not specified", nullable=False)
    payment_deadlines_page = db.Column(db.Integer, nullable=True)
    penalties = db.Column(db.Text, default="Not specified", nullable=False)
    penalties_page = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.String(100), default="Not specified", nullable=False)
    start_date_page = db.Column(db.Integer, nullable=True)
    end_date = db.Column(db.String(100), default="Not specified", nullable=False)
    end_date_page = db.Column(db.Integer, nullable=True)
    renewal_date = db.Column(db.String(100), default="Not specified", nullable=False)
    renewal_date_page = db.Column(db.Integer, nullable=True)
    notice_period = db.Column(db.String(255), default="Not specified", nullable=False)
    notice_period_page = db.Column(db.Integer, nullable=True)
    termination_conditions = db.Column(db.Text, default="Not specified", nullable=False)
    termination_conditions_page = db.Column(db.Integer, nullable=True)
    obligations = db.Column(db.JSON, default=list, nullable=False)
    important_dates = db.Column(db.JSON, default=list, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "analysisId": self.analysis_id,
            "contractAmount": self.contract_amount,
            "contractAmountPage": self.contract_amount_page,
            "paymentDeadlines": self.payment_deadlines,
            "paymentDeadlinesPage": self.payment_deadlines_page,
            "penalties": self.penalties,
            "penaltiesPage": self.penalties_page,
            "startDate": self.start_date,
            "startDatePage": self.start_date_page,
            "endDate": self.end_date,
            "endDatePage": self.end_date_page,
            "renewalDate": self.renewal_date,
            "renewalDatePage": self.renewal_date_page,
            "noticePeriod": self.notice_period,
            "noticePeriodPage": self.notice_period_page,
            "terminationConditions": self.termination_conditions,
            "terminationConditionsPage": self.termination_conditions_page,
            "obligations": self.obligations or [],
            "importantDates": self.important_dates or [],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<ExtractedInformation for analysis {self.analysis_id}>"
