# LexiLegal AI — Migration Plan: From Generative LLM to Interpretable Python NLP

**Document Version**: 1.0.0  
**Target Branch**: `nlp-stack`  
**Base Tag**: `pre-migration` (`commit 723df24`)  
**Scope**: Complete architectural migration from Java 21 / Spring Boot 3 / React 18 / PostgreSQL / Gemini to Flask / MySQL 8 / spaCy / NLTK / sentence-transformers / BERT / Jinja2 / Vanilla JS / Chart.js.

---

## 1. Executive Summary & Migration Rationale

LexiLegal AI was originally prototyped as a distributed microservice application (Spring Boot backend, React single-page app, FastAPI AI engine, and cloud LLMs via Gemini API). While functional, relying on third-party generative LLMs for legal contract simplification introduces critical limitations for an academic and enterprise setting:
1. **Black-Box Opacity**: Cloud LLMs synthesize language without strict span-level traceability, raising the risk of subtle hallucination or dropping vital legal qualifications (e.g. "unless", "subject to").
2. **Third-Party Dependency & Cloud 503 Spikes**: External APIs suffer transient throttling, network latency, and service unavailability.
3. **Data Privacy**: Transmitting confidential corporate contracts and NDAs across third-party cloud boundaries conflicts with strict legal privacy requirements.
4. **Architectural Complexity**: Maintaining three separate runtime environments (Node.js/npm, Java/Maven, Python/FastAPI) alongside dual databases (PostgreSQL and in-memory caches) introduces unnecessary operational overhead.

The target architecture consolidates the entire platform into **one unified, transparent Python 3.11+ Flask application**. All NLP processing (clause classification, fact extraction, tri-tier simplification, risk rule checks, and extractive QA) executes **locally on CPU/GPU** using deterministic, auditable machine learning and rule-based pipelines.

---

## 2. Inventory of Current System

### 2.1 Services & Tech Stack
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide icons, Recharts (Pages: Landing, Login, Register, Dashboard, Upload, Analysis, History, Profile, Simplify Studio).
- **Backend**: Spring Boot 3.3.5, Java 21, Spring Security (Stateless JWT), Spring Data JPA, Flyway migrations, OpenPDF 2.0.3, HikariCP.
- **AI Engine**: FastAPI, Python 3.14, PyMuPDF, Pydantic, Google Gemini API (`gemini-3.5-flash-lite`).
- **Database**: PostgreSQL 16 (10 tables, Flyway migrations `V1__init_schema.sql`, `V2__add_indexes.sql`, `ts_rank` full-text search).

### 2.2 Routes & Endpoints Inventory
| Category | Method | Path | Function |
|---|---|---|---|
| Health | `GET` | `/api/health` | DB connection check |
| Health | `GET` | `/api/health/ai` | AI engine bridge check |
| Auth | `POST` | `/api/auth/register` | User registration |
| Auth | `POST` | `/api/auth/login` | JWT token acquisition |
| User | `GET` | `/api/users/me`, `/api/auth/profile` | Current user profile |
| User | `PUT` | `/api/users/me`, `/api/auth/profile` | Update user profile |
| Document | `POST` | `/api/documents/upload` | Multipart file upload (10MB, PDF/DOCX/TXT) |
| Document | `GET` | `/api/documents` | Paginated documents list |
| Document | `GET` | `/api/documents/{id}` | Single document metadata |
| Document | `GET` | `/api/documents/{id}/status` | Status polling (`UPLOADED` -> `COMPLETED`) |
| Document | `GET` | `/api/documents/{id}/text` | Paginated document plain text |
| Document | `POST` | `/api/documents/{id}/reanalyze`| Trigger pipeline re-run |
| Document | `DELETE`| `/api/documents/{id}` | Cascade document deletion |
| Analysis | `GET` | `/api/documents/{id}/analysis` | Document summary & metadata |
| Analysis | `GET` | `/api/documents/{id}/clauses` | Extracted clauses with 3 simplification tiers |
| Analysis | `POST` | `/api/documents/{id}/clauses/{clauseId}/re-explain` | On-demand clause re-explanation |
| Analysis | `GET` | `/api/documents/{id}/risks` | Color-coded risk findings & questions |
| Analysis | `GET` | `/api/documents/{id}/key-info` | Key facts, dates, currencies |
| Analysis | `GET` | `/api/documents/{id}/missing` | Missing standard provisions |
| Analysis | `GET` | `/api/documents/{id}/report.pdf` | 10-section PDF report dossier |
| Chat | `POST` | `/api/documents/{id}/chat` | RAG question answering |
| Chat | `GET` | `/api/documents/{id}/chat/conversations` | List conversation threads |
| Chat | `GET` | `/api/documents/{id}/chat/conversations/{id}/messages` | Message history with citations |
| Chat | `DELETE`| `/api/documents/{id}/chat/conversations/{id}` | Delete conversation |
| Dashboard | `GET` | `/api/dashboard/stats` | SQL aggregates for current user |
| Studio | `POST` | `/api/simplify` | Standalone text simplification |

### 2.3 Database Schema Inventory
- `users`: id (UUID), email, password_hash, full_name, role, timestamps.
- `documents`: id (UUID), user_id, original_filename, storage_path, file_type, file_size, file_hash, page_count, is_scanned, status, failure_reason, timestamps.
- `document_analyses`: id (UUID), document_id, title, document_type, purpose, parties (JSON), summary_short, summary_detailed, main_conditions (JSON), obligations_summary (JSON), financial_terms_summary (JSON), verification_rate, timestamps.
- `extracted_clauses`: id (UUID), analysis_id, title, category, custom_label, original_text, simplified_simple, simplified_detailed, simplified_professional, importance, affected_party, source_page, section_reference, evidence_quote, quote_verified, provenance, timestamps.
- `risk_findings`: id (UUID), analysis_id, title, category, level, original_clause, explanation, why_it_matters, possible_consequences, source_page, evidence_quote, quote_verified, jurisdiction_caveat, suggested_questions (JSON), provenance, timestamps.
- `extracted_information`: id (UUID), analysis_id, contract_amount, contract_amount_page, payment_deadlines, payment_deadlines_page, penalties, penalties_page, start_date, start_date_page, end_date, end_date_page, renewal_date, renewal_date_page, notice_period, notice_period_page, termination_conditions, termination_conditions_page, obligations (JSON), important_dates (JSON), timestamps.
- `missing_clause_warnings`: id (UUID), analysis_id, category, clause_name, why_it_matters, typical_provision, risk_level, label, timestamps.
- `document_chunks`: id (UUID), document_id, chunk_index, page_number, content, token_count, tsv (FTS vector), timestamps.
- `chat_conversations`: id (UUID), document_id, user_id, title, timestamps.
- `chat_messages`: id (UUID), conversation_id, role, content, citations (JSON), confidence, timestamps.

---

## 3. Directory & File Action Plan (KEEP / ADAPT / REPLACE / REMOVE)

| Path / Component | Action | Details & Migration Strategy |
|---|---|---|
| `samples/contracts/*` | **KEEP** | Retain all 11 evaluation samples (clean NDA, rental, employment, one-sided agreement, DOCX, TXT, scanned, corrupted, etc.). |
| `samples/gold/*` | **KEEP** | Retain ground truth gold files (`clean_nda_gold.json`, `rental_agreement_gold.json`, `employment_agreement_gold.json`, `one_sided_agreement_gold.json`). |
| `evaluation/chat_questions.json` | **KEEP** | Retain 15+ benchmark questions and extend to 25+ questions. |
| `evaluation/results/report_renders/*` | **KEEP** | Retain Phase 9 reference renders for visual regression checking. |
| `ai-engine/app/analyzers/expected_provisions.yaml` | **ADAPT** | Port to `data/expected_provisions.yaml` with enriched document categories. |
| `ai-engine/app/services/extractor.py` | **ADAPT** | Port PyMuPDF and Tesseract extraction logic to `app/nlp/extraction/`. |
| `ai-engine/app/services/chunker.py` | **ADAPT** | Port chunking and page attribution to `app/nlp/segmentation/`. |
| `ai-engine/app/services/quote_verifier.py` | **ADAPT** | Adapt exact substring + Levenshtein fuzzy matching into `app/nlp/qa/` for quote verification. |
| `backend/src/main/resources/db/migration/*` | **ADAPT** | Adapt table schemas into Flask-SQLAlchemy declarative models and Alembic migrations. |
| `backend/src/main/java/com/lexilegal/service/ReportPdfService.java` | **REPLACE** | Replace Java OpenPDF with Python ReportLab (`app/services/report_service.py`) keeping the identical 10-section dossier layout. |
| `backend/` (All Java code & pom.xml) | **REMOVE** | Remove in Phase M10 once Flask backend achieves 100% parity. |
| `frontend/` (All React / Node / Vite code) | **REMOVE** | Remove in Phase M10 once Jinja2 templates and vanilla JS UI are verified. |
| `ai-engine/` (FastAPI / Gemini code) | **REMOVE** | Remove in Phase M10 once unified Flask NLP pipeline passes all benchmarks. |
| `docker-compose.yml` | **REPLACE** | Replace with MySQL 8 service container (optional, standalone MySQL install also supported). |
| `postman/` | **REMOVE** | Obsolete post-migration (Flask app has full test suites and smoke test script). |

---

## 4. Target Stack Architecture

The new system is organized as a single, unified Flask application with clean separation of concerns:

```
lexilegal-ai/
├── app/
│   ├── __init__.py           # Application factory, extensions (DB, Migrate, Login, Limiter, CSRF)
│   ├── config.py             # Environment configuration (.env parsing)
│   ├── models/               # SQLAlchemy models (User, Document, Clause, Risk, KeyInfo, Chat, Chunk)
│   ├── blueprints/           # Thin Flask Blueprints
│   │   ├── auth.py           # Register, login, logout, profile
│   │   ├── documents.py      # Upload, status polling, text preview, delete
│   │   ├── analysis.py       # Summary, clauses, risks, key-info, missing provisions
│   │   ├── chat.py           # RAG chat, conversations, message history
│   │   ├── dashboard.py      # User SQL aggregate statistics
│   │   ├── reports.py        # ReportLab PDF generation and download
│   │   └── studio.py         # Standalone text simplification studio
│   ├── services/             # Core business orchestration
│   │   ├── document_service.py
│   │   ├── analysis_service.py
│   │   ├── chat_service.py
│   │   ├── report_service.py
│   │   └── job_runner.py     # In-app ThreadPoolExecutor background pipeline
│   ├── nlp/                  # Modular, transparent Python NLP package
│   │   ├── extraction/       # PyMuPDF, python-docx, Tesseract OCR
│   │   ├── segmentation/     # Punkt sentence splitting, heading/clause segmentation, character offsets
│   │   ├── classification/   # Ensemble: BERT on LEDGAR + SBERT zero-shot + keyword rules
│   │   ├── entities/         # spaCy NER + EntityRuler for legal terms, dates, amounts
│   │   ├── summarization/    # SBERT TextRank + Maximal Marginal Relevance (extractive)
│   │   ├── simplification/   # Rule-based 3-tier simplifier (150+ term glossary, dependency parse splitting)
│   │   ├── risk/             # Rule-based patterns + SBERT prototype similarity + Rule 7 filter
│   │   ├── retrieval/        # Hybrid search: SBERT cosine + MySQL FULLTEXT (RRF fusion)
│   │   ├── qa/               # Extractive BERT QA (SQuAD 2.0 with no-answer threshold)
│   │   └── registry.py       # Centralized, lazy-loaded model singleton manager
│   ├── templates/            # Jinja2 templates (base, auth, dashboard, upload, analysis, reports)
│   └── static/
│       ├── css/style.css     # Hand-written CSS design tokens, light/dark mode variables
│       ├── js/               # Vanilla JavaScript modules (upload, status polling, tabs, chat)
│       └── vendor/           # Local Chart.js (v4.x, zero external CDN)
├── data/
│   ├── glossary.yaml         # 150+ legal terms with plain-English definitions
│   ├── risk_rules.yaml       # Pattern and entity criteria for contract risks
│   ├── expected_provisions.yaml # Standard expected clause checklists by document type
│   ├── clause_prototypes.yaml   # SBERT prototype descriptions for zero-shot clause scoring
│   └── label_mapping.json    # LEDGAR 100+ categories mapped to 21 target categories
├── training/
│   ├── train_clause_classifier.py # Hugging Face Trainer script for LEDGAR fine-tuning
│   └── evaluate_models.py    # Offline evaluation of NLP models
├── evaluation/
│   ├── baseline_llm/         # Pre-migration reference outputs from Gemini 3.5 Flash Lite
│   ├── results/              # Post-migration benchmark metrics and confusion matrices
│   └── RESULTS.md            # Final evaluation benchmark documentation
├── scripts/
│   ├── download_models.py    # Downloads and caches BERT, SBERT, and spaCy models
│   ├── smoke_test.py         # End-to-end HTTP smoke test
│   ├── style_check.py        # Enforces human-written style, banned words, and comment density
│   └── leftover_check.py     # Verifies zero legacy stack artifacts remain
├── requirements.txt
├── .env.example
└── README.md
```

---

## 5. Model Selection & Fallback Matrix

| NLP Capability | Primary Model | Fallback / Offline Model | Download Size | Device / RAM Budget |
|---|---|---|---|---|
| Linguistic Parsing & NER | `en_core_web_md` (spaCy 3.7+) | `en_core_web_sm` | 40 MB / 12 MB | CPU / ~250 MB |
| Dense Sentence Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Cached local weights | ~90 MB | CPU / ~350 MB |
| Clause Classification | Fine-tuned DistilBERT on LEDGAR (`models/clause_classifier`) | SBERT Zero-Shot + Keyword Rules | ~260 MB | CPU / ~500 MB |
| Extractive Question Answering | `deepset/bert-base-uncased-squad2` (or `distilbert-base-cased-distilled-squad`) | Keyword & Stored Fact Intent Router | ~260 MB | CPU / ~600 MB |
| **Total Model Footprint** | | | **~650 MB** | **~1.7 GB Total RAM** |

---

## 6. Migration Phase Breakdown & Gate Criteria

- **Phase M0 — Inventory, Safety Net & Baseline**:
  - Clean working tree, tag `pre-migration`, branch `nlp-stack`.
  - Comprehensive `docs/migration-plan.md`, `docs/parity.md`, `docs/PROGRESS.md`.
  - Capture baseline LLM outputs for sample contracts in `evaluation/baseline_llm/`.
  - Verify toolchain (Python 3.11+, MySQL 8/Docker, Tesseract, Git).
  - *Gate*: Baseline outputs captured; plan approved.
- **Phase M1 — Flask Skeleton, MySQL & Authentication**:
  - Flask app factory, SQLAlchemy models, Alembic migrations, Flask-Login, Flask-WTF CSRF, Flask-Limiter.
  - Hand-written CSS design tokens, light/dark mode, base template, auth pages.
  - *Gate*: Migrations apply to empty MySQL DB; all auth tests pass; browser verification.
- **Phase M2 — Ingestion, Extraction, OCR & Clause Segmentation**:
  - Port PyMuPDF, python-docx, Tesseract OCR, upload validation (magic bytes, 10MB ceiling).
  - Clause segmentation with exact character offsets (`original_text` is an exact source slice).
  - Background ThreadPoolExecutor status stepper (`UPLOADED` -> `COMPLETED`).
  - *Gate*: All contract sample formats pass; clause offsets match source slices; 404 tenant isolation verified.
- **Phase M3 — Embeddings, Document Type & Clause Classification**:
  - `registry.py` lazy-loaded model manager and `download_models.py`.
  - SBERT document type classification.
  - LEDGAR fine-tuned BERT + SBERT prototype + keyword voting ensemble.
  - Clauses tab UI with category/importance filters, search, and provenance badges.
  - *Gate*: Macro-F1 reported; fallback works if fine-tuned weights missing; UI filters functional.
- **Phase M4 — Entities, Key Facts & Extractive Summarization**:
  - spaCy NER + EntityRuler for money (₹/Rs./$), dates, durations, parties.
  - Rule 6 strict `"Not specified"` default.
  - SBERT TextRank + MMR extractive summarization.
  - *Gate*: Summary sentences exist verbatim in source; key facts match gold annotations.
- **Phase M5 — Rule-Based Simplification & Readability**:
  - 150+ term legal glossary (`data/glossary.yaml`), modal verb rewrites, dependency-parse sentence splitting.
  - 3 modes: Simple English, Detailed template, Professional structured breakdown.
  - Negation and condition preservation checker with fallback to original text.
  - *Gate*: At least 20 legal passages tested; Flesch reading ease score improves on average.
- **Phase M6 — Risk Detection & Missing Provisions**:
  - Rule-based risk engine (`data/risk_rules.yaml`) + SBERT prototype similarity.
  - Rule 7 non-definitive phrasing enforcement (no "illegal" or "void").
  - Document-type checklist comparison for missing provisions with `"Possible omission"` label.
  - Local Chart.js risk distribution visualizations.
  - *Gate*: Predatory clauses detected in one-sided sample; 0 Rule 7 violations; charts match SQL aggregates.
- **Phase M7 — Hybrid Retrieval & Extractive QA Document Chat**:
  - Hybrid retrieval: SBERT cosine similarity + MySQL FULLTEXT (RRF ranking).
  - Extractive BERT QA with SQuAD 2.0 no-answer threshold.
  - Intent routing for stored key facts (amounts, deadlines, penalties).
  - *Gate*: 25+ questions tested; honest refusal on unanswerable questions; prompt injection resistance.
- **Phase M8 — Dashboard, ReportLab PDF Dossier & UI Polish**:
  - Real SQL aggregates for dashboard (zero hardcoded values).
  - ReportLab 10-section PDF report builder with TrueType Unicode fonts (₹, §, curly quotes).
  - Finish remaining Jinja2 templates (History, Profile).
  - *Gate*: Dashboard numbers match manual SQL; 3 sample reports rendered and inspected; tenant isolation verified.
- **Phase M9 — Comprehensive Evaluation & RESULTS.md**:
  - Full evaluation suite across all 6+ gold documents.
  - Old LLM vs. New NLP comparison tables, confusion matrices, and latency/RAM profiling.
  - *Gate*: `evaluation/RESULTS.md` completed with real metrics and single-command execution script.
- **Phase M10 — Legacy Removal, Hardening & Final Gate**:
  - Remove `frontend/`, `backend/`, `ai-engine/`, and legacy configs.
  - Security review, restart recovery, `style_check.py`, and `leftover_check.py`.
  - Fresh-clone dry run.
  - *Gate*: All tests pass, style and leftover checks 100% clean.
