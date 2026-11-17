# Project Progress Log

This log summarizes the milestones completed for LexiLegal AI. Historical details on the earlier multi-service prototype are recorded in [MIGRATION_NOTES.md](MIGRATION_NOTES.md).

## Completed milestones

1. **Core Flask app, MySQL schema, and auth**: Set up the Flask app factory, 10 SQLAlchemy tables with Alembic migrations, Flask-Login session auth, scrypt password hashing, CSRF protection, rate limiting, and per-user isolation (`404` on cross-user access).
2. **Document extraction and segmentation**: Implemented PDF extraction via PyMuPDF (with `INFINITE_RECT()` to prevent right-margin clipping), DOCX extraction via `python-docx`, Tesseract OCR fallback for low-text pages, magic-byte validation, SHA-256 duplicate checks, and exact character-offset clause segmentation.
3. **Clause and document classification**: Built the ensemble classifier combining LEDGAR DistilBERT, SBERT prototypes, and keyword rules across 17 categories plus `Other`, along with importance scoring and spaCy subject extraction.
4. **Key information and extractive summaries**: Added entity extraction for currency amounts (`$`, `₹`, `€`, `Rs.`), dates, notice periods, late fees, and parties, defaulting missing fields to `"Not specified"`. Implemented SBERT TextRank + MMR extractive summarization.
5. **Plain-language simplification and studio**: Built the `app/nlp/simplification/` package (151-term glossary, modal rewrites, sentence splitting, three explanation modes, trap checks, and pure-Python Flesch readability scores) and the `/studio` page.
6. **Risk detection and missing provisions**: Added YAML risk rules, semantic prototype checks, `soften_legal_claims()` to avoid absolute legal conclusions, and per-document-type omission checklists labeled `"Possible omission"`.
7. **Document Q&A**: Implemented hybrid retrieval (SBERT + BM25 RRF), a deterministic fact intent router, and `deepset/minilm-uncased-squad2` extractive QA with an unanswerable refusal threshold and page citations.
8. **Dashboard, PDF reports, and UI rework**: Wired per-user SQL dashboard aggregates with local Chart.js, built the 10-section ReportLab PDF report with local TrueType fonts, and reworked the stylesheet and templates with local Liberation Serif headings, 1px borders, dark mode contrast, and zero horizontal overflow at 390px, 768px, and 1440px.
9. **Offline evaluation and cleanup**: Built `evaluation/evaluate_nlp_stack.py` (`evaluation/RESULTS.md`), `scripts/snapshot.py` for behavior-diff verification, thin split blueprints (`documents`, `analysis`, `chat`, `reports`), and `scripts/style_check.py`.

## Verification commands

```bash
.venv/bin/pytest tests/ --cov=app -q
.venv/bin/ruff check app tests scripts evaluation/evaluate_nlp_stack.py
.venv/bin/black --check app tests scripts evaluation/evaluate_nlp_stack.py
.venv/bin/python evaluation/evaluate_nlp_stack.py
.venv/bin/python scripts/style_check.py
```
