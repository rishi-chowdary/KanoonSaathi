"""Risk detection and missing-provision checklist persistence."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.extensions import db
from app.models.analysis import DocumentAnalysis
from app.models.clause import ExtractedClause
from app.models.document import Document
from app.models.missing_warning import MissingClauseWarning
from app.models.risk import RiskFinding
from app.nlp.missing_provisions import detect_missing_provisions
from app.nlp.risk_engine import detect_clause_risks

logger = logging.getLogger("lexilegal.services.risk_service")


def process_document_risks_and_missing(
    doc: Document,
    analysis: DocumentAnalysis,
    clauses: list[ExtractedClause],
    full_text: str,
) -> tuple[list[RiskFinding], list[MissingClauseWarning]]:
    """Evaluate contract risks and missing provisions, persisting findings to database."""
    # 1. Determine if governing law is explicitly established
    governing_law_stated = any(
        c.category == "GOVERNING_LAW" or "governing law" in c.title.lower()
        for c in clauses
    )

    # 2. Detect contractual risks
    risk_dicts = detect_clause_risks(
        clauses=clauses,
        full_text=full_text,
        governing_law_stated=governing_law_stated,
    )

    # Clear previous risks for idempotency
    RiskFinding.query.filter_by(analysis_id=analysis.id).delete()

    created_risks: list[RiskFinding] = []
    for r in risk_dicts:
        risk_model = RiskFinding(
            id=str(uuid.uuid4()),
            analysis_id=analysis.id,
            category=r["category"],
            level=r["level"],
            title=r["title"],
            original_clause=r["original_clause"],
            explanation=r["explanation"],
            why_it_matters=r["why_it_matters"],
            possible_consequences=r["possible_consequences"],
            suggested_questions=r["suggested_questions"],
            source_page=r["source_page"],
            evidence_quote=r["evidence_quote"],
            quote_verified=r["quote_verified"],
            jurisdiction_caveat=r["jurisdiction_caveat"],
            provenance=r["provenance"],
        )
        db.session.add(risk_model)
        created_risks.append(risk_model)

    # 3. Detect missing expected provisions
    missing_dicts = detect_missing_provisions(
        clauses=clauses,
        document_type=analysis.document_type or "",
        full_text=full_text,
    )

    # Clear previous missing warnings
    MissingClauseWarning.query.filter_by(analysis_id=analysis.id).delete()

    created_missing: list[MissingClauseWarning] = []
    for m in missing_dicts:
        warning_model = MissingClauseWarning(
            id=str(uuid.uuid4()),
            analysis_id=analysis.id,
            category=m["category"],
            clause_name=m["clause_name"],
            why_it_matters=m["why_it_matters"],
            typical_provision=m["typical_provision"],
            risk_level=m["risk_level"],
            label="Possible omission",
        )
        db.session.add(warning_model)
        created_missing.append(warning_model)

    db.session.commit()

    logger.info(
        "Successfully identified %d risks and %d missing provisions for document %s.",
        len(created_risks),
        len(created_missing),
        doc.id,
    )

    return created_risks, created_missing


def get_risk_distribution(analysis_id: str) -> dict[str, Any]:
    """Calculate aggregate risk counts by level and category for Chart.js visualization."""
    risks = RiskFinding.query.filter_by(analysis_id=analysis_id).all()

    by_level = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFORMATIONAL": 0}
    by_category: dict[str, int] = {}

    for r in risks:
        by_level[r.level] = by_level.get(r.level, 0) + 1
        by_category[r.category] = by_category.get(r.category, 0) + 1

    return {
        "totalRisks": len(risks),
        "byLevel": by_level,
        "byCategory": by_category,
    }
