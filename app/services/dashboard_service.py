"""LexiLegal AI — Dashboard Service.

Computes genuine SQL aggregate statistics and risk distributions strictly partitioned
by user ID to ensure complete multi-tenant data isolation. Zero hardcoded metrics.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import func

from app.extensions import db
from app.models.analysis import DocumentAnalysis
from app.models.clause import ExtractedClause
from app.models.document import Document
from app.models.risk import RiskFinding

logger = logging.getLogger("lexilegal.dashboard_service")


def get_dashboard_stats(user_id: str) -> dict[str, Any]:
    """Retrieve full dashboard statistics for the specified user via direct SQL queries."""
    total_docs = Document.query.filter_by(user_id=user_id).count()

    analyzed_docs = Document.query.filter(
        Document.user_id == user_id,
        Document.status.in_(
            ["COMPLETED", "COMPLETED_WITH_WARNINGS", "ANALYZED", "EXTRACTED"]
        ),
    ).count()

    failed_docs = Document.query.filter_by(user_id=user_id, status="FAILED").count()

    total_clauses = (
        db.session.query(func.count(ExtractedClause.id))
        .join(DocumentAnalysis, ExtractedClause.analysis_id == DocumentAnalysis.id)
        .join(Document, DocumentAnalysis.document_id == Document.id)
        .filter(Document.user_id == user_id)
        .scalar()
        or 0
    )

    total_risks = (
        db.session.query(func.count(RiskFinding.id))
        .join(DocumentAnalysis, RiskFinding.analysis_id == DocumentAnalysis.id)
        .join(Document, DocumentAnalysis.document_id == Document.id)
        .filter(Document.user_id == user_id)
        .scalar()
        or 0
    )

    avg_verif = (
        db.session.query(func.avg(DocumentAnalysis.verification_rate))
        .join(Document, DocumentAnalysis.document_id == Document.id)
        .filter(Document.user_id == user_id)
        .scalar()
    )
    avg_verification_rate = round(float(avg_verif), 1) if avg_verif is not None else 0.0

    level_counts = (
        db.session.query(RiskFinding.level, func.count(RiskFinding.id))
        .join(DocumentAnalysis, RiskFinding.analysis_id == DocumentAnalysis.id)
        .join(Document, DocumentAnalysis.document_id == Document.id)
        .filter(Document.user_id == user_id)
        .group_by(RiskFinding.level)
        .all()
    )
    risk_level_map = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFORMATIONAL": 0}
    for lvl, count in level_counts:
        if lvl and str(lvl).upper() in risk_level_map:
            risk_level_map[str(lvl).upper()] = int(count)

    category_counts = (
        db.session.query(RiskFinding.category, func.count(RiskFinding.id))
        .join(DocumentAnalysis, RiskFinding.analysis_id == DocumentAnalysis.id)
        .join(Document, DocumentAnalysis.document_id == Document.id)
        .filter(Document.user_id == user_id)
        .group_by(RiskFinding.category)
        .all()
    )
    risk_category_map = {str(cat): int(count) for cat, count in category_counts if cat}

    recent_docs = (
        Document.query.filter_by(user_id=user_id)
        .order_by(Document.created_at.desc())
        .limit(5)
        .all()
    )
    recent_doc_items = [
        {
            "id": d.id,
            "filename": d.original_filename,
            "fileType": d.file_type,
            "fileSize": d.file_size,
            "status": d.status,
            "pageCount": d.page_count,
            "createdAt": d.created_at.isoformat() if d.created_at else None,
        }
        for d in recent_docs
    ]

    recent_analyses = (
        db.session.query(DocumentAnalysis)
        .join(Document, DocumentAnalysis.document_id == Document.id)
        .filter(Document.user_id == user_id)
        .order_by(DocumentAnalysis.created_at.desc())
        .limit(5)
        .all()
    )
    recent_analysis_items = [
        {
            "id": a.id,
            "documentId": a.document_id,
            "documentType": a.document_type,
            "verificationRate": float(a.verification_rate or 0.0),
            "createdAt": a.created_at.isoformat() if a.created_at else None,
        }
        for a in recent_analyses
    ]

    return {
        "totalDocuments": total_docs,
        "analyzedDocuments": analyzed_docs,
        "failedDocuments": failed_docs,
        "totalClauses": total_clauses,
        "totalRisks": total_risks,
        "averageVerificationRate": avg_verification_rate,
        "riskDistributionByLevel": risk_level_map,
        "riskDistributionByCategory": risk_category_map,
        "recentDocuments": recent_doc_items,
        "recentAnalyses": recent_analysis_items,
    }
