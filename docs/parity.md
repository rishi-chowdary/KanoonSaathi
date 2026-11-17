# Feature Coverage Matrix

This table maps each capability in LexiLegal AI to its local Python implementation and the automated test that checks it. Background on the earlier multi-service prototype is kept in [MIGRATION_NOTES.md](MIGRATION_NOTES.md).

| Area | Local implementation | Automated check |
|---|---|---|
| Database schema & cascades | MySQL 8 (`InnoDB`, `utf8mb4`), 10 SQLAlchemy tables, Alembic | `tests/test_database.py` |
| Auth, sessions, CSRF, rate limits | Flask-Login (`HttpOnly`, `SameSite=Lax`), scrypt hashes, Flask-WTF, Flask-Limiter | `tests/test_auth.py` |
| Upload validation & deduplication | Extension check, magic bytes (`%PDF`, `PK\x03\x04`), 10 MB limit, per-user SHA-256 | `tests/test_extraction.py`, `tests/test_ingestion_api.py` |
| Text extraction & OCR | PyMuPDF (`fitz`), `python-docx`, UTF-8 text, Tesseract OCR fallback | `tests/test_extraction.py` |
| Clause segmentation & offsets | Heading regex + legal-abbreviation NLTK `punkt`; exact `text[start:end]` slicing | `tests/test_segmentation.py` |
| Document & clause classification | LEDGAR DistilBERT + SBERT prototypes + keyword rules; fallback to `Other` | `tests/test_clause_classification.py` |
| Importance & affected party | Category weight + obligation verbs + spaCy dependency subjects | `tests/test_clause_classification.py` |
| Key info & absent defaults | spaCy NER + regex + `dateparser`; missing fields return `"Not specified"` | `tests/test_entities_and_summary.py` |
| Extractive summaries | SBERT TextRank + Maximal Marginal Relevance (MMR) | `tests/test_entities_and_summary.py` |
| Simplification & readability | `app/nlp/simplification/` (151-term glossary, templates, trap checks) + Flesch scores | `tests/test_simplifier.py` |
| Risk detection & wording filter | `data/risk_rules.yaml` + SBERT prototypes + `soften_legal_claims()` | `tests/test_risk.py` |
| Missing provisions | `data/expected_provisions.yaml` + SBERT check; tagged `"Possible omission"` | `tests/test_risk.py` |
| Hybrid retrieval & extractive QA | SBERT + BM25 (RRF, `k=60`) + fact router + `minilm-uncased-squad2` refusal check | `tests/test_qa.py` |
| Per-user isolation | `user_id == current_user.id` on every query; cross-user lookup returns `404` | `tests/test_qa.py`, `tests/test_dashboard_and_report.py` |
| Dashboard SQL aggregates & charts | SQLAlchemy `func.count` queries + local Chart.js (`app/static/vendor/chart.js`) | `tests/test_dashboard_and_report.py` |
| PDF report export | ReportLab 10-section PDF with local TrueType fonts and `Page X of Y` footers | `tests/test_dashboard_and_report.py` |
| Offline evaluation benchmark | `evaluation/evaluate_nlp_stack.py` producing `evaluation/RESULTS.md` | `tests/test_evaluation.py` |
| End-to-end HTTP lifecycle | Register -> upload -> clauses -> risks -> Q&A -> PDF -> delete | `tests/test_smoke_flow.py`, `scripts/smoke_test.sh` |
