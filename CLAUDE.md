# LexiLegal AI — Developer Notes

## Overview

LexiLegal AI is a B.Tech Data Science project built as a single local Flask application backed by MySQL 8 and an offline Python NLP stack. Users upload a legal contract (PDF, DOCX, or TXT) and get extracted text with page numbers, an extractive summary, categorized clauses with three rule-based simplification modes, risk flags, key facts, missing-provision notes, a 10-section PDF report, and extractive document Q&A.

No generative LLMs or hosted AI APIs are used anywhere in the application.

## Stack

- **Web**: Python 3.11+, Flask (app factory + blueprints), Flask-SQLAlchemy, Flask-Migrate (Alembic), Flask-Login, Flask-WTF (CSRF), Flask-Limiter
- **Database**: MySQL 8 (`utf8mb4`, `InnoDB`) via PyMySQL
- **Local NLP**: spaCy (`en_core_web_md`), NLTK (`punkt`), `sentence-transformers` (`all-MiniLM-L6-v2`), Hugging Face `transformers` + PyTorch (LEDGAR DistilBERT, `deepset/minilm-uncased-squad2`), scikit-learn, numpy
- **Extraction and PDF**: PyMuPDF, `python-docx`, `pytesseract` + Pillow, ReportLab
- **Frontend**: Jinja2 templates, hand-written CSS with local Liberation Serif fonts, vanilla JS, local Chart.js (`app/static/vendor/chart.js`)
- **Checks**: pytest, pytest-cov, ruff, black, `scripts/style_check.py`, `scripts/snapshot.py`

## Layout

```text
lexilegal-ai/
  app/
    __init__.py, config.py, extensions.py
    models/         (10 SQLAlchemy tables)
    blueprints/     (auth, documents, analysis, chat, reports, studio, main, guards)
    services/       (document, analysis, clause, risk, chat, dashboard, report)
    nlp/            (extraction, segmentation, clause_classifier, document_classifier,
                     evidence, importance, parties, key_info, summarizer,
                     simplification/, readability, risk_engine, missing_provisions,
                     retrieval, qa_engine, registry)
    templates/      (Jinja2 views)
    static/         (style.css, main.js, fonts/, img/, vendor/chart.js)
  data/             (glossary.yaml, indian_statutes.yaml, risk_rules.yaml, expected_provisions.yaml, clause_prototypes.yaml, clause_rules.yaml)
  migrations/       (Alembic migrations)
  samples/          (Indian contracts, BNS/IPC/Constitution PDFs, and gold annotations)
  evaluation/       (evaluate_nlp_stack.py, evaluate_clauses.py, RESULTS.md, chat_questions.json, results/)
  tests/            (106 pytest tests)
  scripts/          (download_models.py, generate_indian_samples.py, smoke_test.sh, style_check.py)
  docs/             (architecture.md, api-documentation.md, privacy.md, DEMO.md)
```

## Core invariants

1. **Exact source slicing**: Extracted clauses and evidence quotes store exact source offsets (`start_char`, `end_char`, `page_start`, `page_end`). `quote_verified` checks substring/offset matching against the extracted text.
2. **Absent field defaults**: Missing key-info fields default to `"Not specified"` — never invent dates, amounts, or parties.
3. **Non-definitive risk wording**: `soften_legal_claims()` in `app/nlp/risk_engine.py` avoids absolute conclusions ("illegal", "void", "unenforceable", "unlawful"). Missing-provision checks are labeled `"Possible omission"`.
4. **Honest Q&A refusal**: When extractive QA falls below threshold (`span_score - null_score < 0.0`), return `"The document does not appear to address this."` with no fabricated citations.
5. **User isolation**: Every document query checks `user_id == current_user.id` and returns `404` on cross-user access.
6. **Local execution**: All models run locally from disk; zero bytes leave the host.

## Style conventions

- Keep routes thin; put logic in `app/services/` and `app/nlp/`.
- Write comments only when explaining a non-obvious why (regex edge case, threshold choice, OCR workaround).
- Prefer plain functions over single-method classes.
- Keep UI plain: 1px borders, small radii (max 8px), no gradients, no backdrop blur, no emoji in source/templates/docs.
- Run `ruff check`, `black --check`, `scripts/style_check.py`, and `pytest tests/ --cov=app -q` before committing.
