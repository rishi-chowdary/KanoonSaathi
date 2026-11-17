# PROJECT: LexiLegal AI — Legal Document Simplification & Important-Clause Extraction

## ROLE
You are a senior engineer acting as: full-stack Python developer, NLP engineer, database designer, and UI/UX developer. You are maintaining a complete, working, college-level B.Tech Data Science project built on a pure local Python NLP stack. It must be demonstrable on a laptop, explainable in a viva, 100% offline-capable, and free to run.

## MISSION
Users upload a legal document (PDF, DOCX, TXT). The system extracts text with page numbers, then produces: extractive summary, important clauses with plain-language explanations (3 modes), grounded risk findings, key facts (amounts, dates, notice periods), missing-clause warnings, a downloadable 10-section PDF report, and a document-grounded chat. Every claim must be traceable to exact source slices in the document.

## PRIORITIES (in order)
1. Working, verified functionality (no placeholders in core features)
2. Grounding and honesty (100% exact source slices, no invented contract terms, ever)
3. Clean, simple, explainable NLP architecture (no black-box generative LLMs)
4. Free, local, zero-API-cost execution
5. Professional UI and demo experience
6. Documentation and tests

## NON-GOALS & FORBIDDEN COMPONENTS
- No generative LLMs or hosted AI APIs (no Gemini, OpenAI, Anthropic, Ollama)
- No React/Node/Vite/Tailwind/shadcn, Java/Maven/Spring, FastAPI, PostgreSQL, Redis/Celery/Kafka, or vector databases

## TECH STACK
- **Web Framework**: Python 3.11+, Flask (app factory + blueprints), Flask-SQLAlchemy, Flask-Migrate (Alembic), Flask-Login, Flask-WTF (CSRF), Flask-Limiter
- **Database**: MySQL 8 (`utf8mb4`, InnoDB) via PyMySQL
- **Local NLP & ML**: spaCy (`en_core_web_md`, fallback `en_core_web_sm`), NLTK (`punkt`), `sentence-transformers` (`all-MiniLM-L6-v2`), Hugging Face `transformers` + PyTorch (`deepset/minilm-uncased-squad2` for extractive QA, DistilBERT LEDGAR support), scikit-learn, numpy, pandas
- **Extraction & Reports**: PyMuPDF, python-docx, pytesseract + Pillow (OCR), ReportLab (10-section PDF dossier with TrueType Unicode fonts)
- **Frontend**: Jinja2 templates, hand-written CSS (light/dark themes), vanilla JavaScript, local static Chart.js (`app/static/vendor/chart.js`, zero CDN)
- **Quality & Testing**: pytest, pytest-cov, ruff, black

## ARCHITECTURE
Single monolithic Flask application. Routes stay thin; logic lives in `app/services/` and `app/nlp/`.
- **App Factory** (`app/__init__.py`): initializes SQLAlchemy, Alembic migrations, Flask-Login, CSRFProtect, Limiter, and startup job crash recovery.
- **Model Registry** (`app/nlp/registry.py`): loads spaCy, SBERT, QA, and classifier models once as thread-safe singletons.
- **Background Jobs**: `ThreadPoolExecutor` inside the app (no Celery). Statuses: `UPLOADED` → `EXTRACTING` → `ANALYZING` → `COMPLETED` | `COMPLETED_WITH_WARNINGS` | `FAILED`.
- **Caching / Deduplication**: SHA-256 hash stored per user to detect identical uploads.
- **Hybrid Chat Retrieval**: SBERT dense semantic embeddings + BM25 sparse lexical search merged via Reciprocal Rank Fusion (RRF, k=60), followed by deterministic fact intent routing and `deepset/minilm-uncased-squad2` extractive QA with SQuAD 2.0 unanswerable refusal thresholding.

## NLP QUALITY RULES (the heart of the project)
1. **EXACT SOURCE SLICING (100% Quote Verification)**: Every extracted clause stores `start_char`, `end_char`, `page_start`, `page_end`, and `original_text` as an exact slice of the source document. `quote_verified` is verified directly via substring/offset matching.
2. **PROVENANCE LABELS**: Every output field is explicitly labeled as `EXTRACTED` (quoted directly from the document) or `RULE_BASED` (simplification, risk reasoning, suggestions) across the UI and PDF report.
3. **OPEN-ENDED CLAUSES**: The ensemble classifier (LEDGAR BERT + SBERT prototypes + keyword rules) maps to 17+ named categories plus `Other` with a descriptive label.
4. **RULE 6 — MISSING FIELDS**: Return exactly `"Not specified"` — never guess dates, amounts, or parties.
5. **RULE 7 — NO LEGAL CONCLUSIONS**: Never say a clause is "illegal", "void", or "unenforceable". Use non-definitive advisory phrasing ("may be unfavorable", "you may want to ask about..."). Missing-clause findings are strictly labeled `"Possible omission"`.
6. **PROMPT-INJECTION DEFENSE**: Document text is treated strictly as untrusted data; output HTML is escaped and there is no generative LLM to hijack.
7. **CHAT HONESTY**: Answer strictly from retrieved passages or verified facts. When confidence is below threshold, return `"The document does not appear to address this."` Always cite exact page numbers.
8. **PRIVACY**: 100% local on-premise execution. Zero bytes leave the machine. Documented in `docs/privacy.md`.

## FEATURES (functional scope)
- **Summary**: Extractive summary via SBERT TextRank + Maximal Marginal Relevance (MMR), plus structured document metadata.
- **Clause Extraction & Tri-Tier Simplification**: Exact clause segmentation + ensemble classification + 3 rule-based modes (Simple English with 151-term glossary, Detailed category template, Professional structured breakdown) with pure-Python Flesch Reading Ease / Kincaid Grade scoring.
- **Risk Identification**: Deterministic YAML rules (`data/risk_rules.yaml`) + SBERT prototype matching + numeric threshold checks with Rule 7 guardrails.
- **Key Information**: spaCy NER + regex + `dateparser` for contract amounts (₹, $, €, Rs.), deadlines, late interest, start/end/renewal dates, notice periods, and parties.
- **Missing-Clause Detection**: Expected provisions checklist per document type (`data/expected_provisions.yaml`) + SBERT similarity check; labeled `"Possible omission"`.
- **Document Chat**: Hybrid retrieval (SBERT + BM25 RRF) + fact intent routing + `minilm-uncased-squad2` extractive QA with conversation persistence.
- **Dashboard**: Real MySQL aggregate queries per user (zero hardcoded numbers) + local Chart.js distribution charts.
- **PDF Report**: 10-section ReportLab dossier with TrueType Unicode fonts (`₹`, `§`, curly quotes), `Page X of Y` footers, and provenance badges.
- **Auth**: Flask-Login sessions (`HttpOnly`, `SameSite=Lax`), scrypt password hashing, CSRF protection, rate limiting, and strict per-user tenant isolation (cross-user queries return `404`).

## PROJECT STRUCTURE
```text
lexilegal-ai/
  app/
    __init__.py, config.py, extensions.py
    models/         (10 SQLAlchemy tables)
    blueprints/     (auth, documents, main, studio)
    services/       (document, analysis, clause, risk, chat, dashboard, report)
    nlp/            (extraction, segmentation, clause_classifier, document_classifier,
                     evidence, importance, parties, key_info, summarizer,
                     simplifier, readability, risk_engine, missing_provisions,
                     retrieval, qa_engine, registry)
    templates/      (Jinja2 views)
    static/         (hand-written CSS, vanilla JS, local vendor/chart.js)
  data/             (glossary.yaml, risk_rules.yaml, expected_provisions.yaml, clause_prototypes.yaml)
  migrations/       (Alembic migrations)
  samples/          (demo legal documents + gold annotation files)
  evaluation/       (evaluate_nlp_stack.py, RESULTS.md, baseline_llm/, results/)
  tests/            (95 automated pytest unit, integration, evaluation, and smoke tests)
  scripts/          (download_models.py, smoke_test.sh)
  docs/             (architecture.md, api-documentation.md, privacy.md, parity.md, DEMO.md, PROGRESS.md)
  postman/          (lexilegal.postman_collection.json)
  run.py, run_local.sh, docker-compose.yml, requirements.txt, README.md, .env.example
```

## HUMAN-WRITTEN STYLE
- Comments: write them rarely, only to explain WHY something non-obvious is done. Never restate what the code does.
- Simplicity over cleverness: prefer plain functions over classes when state isn't needed.
- Formatting enforced by tools: `ruff check` and `black --check`.
- No dead code, no unused imports, no secrets committed.

## DEFINITION OF DONE
Fresh clone → follow `README.md` → `./run_local.sh` → register, upload sample contract, view verified clauses, risks, key facts, chat with citations, download 10-section PDF report → all 95 automated tests pass (`pytest tests/ --cov=app`) → offline benchmark produces `evaluation/RESULTS.md`.
