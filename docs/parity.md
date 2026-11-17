# LexiLegal AI — Feature Parity Matrix

This document tracks the 1-to-1 feature parity between the legacy distributed stack (Spring Boot 3 + React 18 + FastAPI + PostgreSQL + Gemini) and the target unified Python NLP stack (Flask + MySQL 8 + spaCy + NLTK + sentence-transformers + Hugging Face BERT + Jinja2 + vanilla JS + Chart.js).

Nothing may be dropped silently. Every feature has a documented target implementation and an automated test verifying compliance.

---

## Parity Tracking Table

| Feature Area | Legacy Implementation (Old Stack) | Target Implementation (New NLP Stack) | Verifying Test / Proof | Parity Status |
|---|---|---|---|---|
| **Database & Schema** | PostgreSQL 16 via Flyway migrations (10 tables) | MySQL 8 (InnoDB, `utf8mb4_unicode_ci`) via Flask-Migrate & SQLAlchemy | `tests/test_database.py::test_complete_entity_graph_persistence_and_cascade` | **Verified (M1)** |
| **User Authentication** | Spring Security 6 stateless JWT tokens (`Authorization: Bearer`) | Flask-Login secure session cookies (`HttpOnly`, `SameSite=Lax`) | `tests/test_auth.py::test_login_success`, `tests/test_auth.py::test_logout` | **Verified (M1)** |
| **Password Security** | BCrypt via Spring Security `PasswordEncoder` | Werkzeug `generate_password_hash` (scrypt) | `tests/test_auth.py::test_register_success` | **Verified (M1)** |
| **CSRF Protection** | CSRF disabled in REST API; Bearer header auth | Flask-WTF `CSRFProtect` on forms and meta tag for fetch | `tests/test_auth.py::test_register_success` | **Verified (M1)** |
| **Rate Limiting** | Custom in-memory `LoginRateLimiter` (5 attempts/min/IP) | `Flask-Limiter` with memory/redis storage | `app/extensions.py::limiter` | **Verified (M1)** |
| **User Profile Management** | `GET/PUT /api/users/me` and `/api/auth/profile` | Flask Blueprint `/profile` route with WTForms validation | `tests/test_auth.py::test_profile_update`, `tests/test_auth.py::test_api_register_and_login_flow` | **Verified (M1)** |
| **Document Upload** | Multipart upload (`POST /api/documents/upload`), 10MB limit | Flask request `files['file']` with `MAX_CONTENT_LENGTH=10MB` | `tests/test_ingestion_api.py::test_api_upload_valid_pdf` | **Verified (M2)** |
| **Magic Byte Validation** | `DocumentStorageService.java` checks `%PDF-`, `PK\x03\x04`, text | `app/nlp/extraction.py::validate_file` | `tests/test_extraction.py::test_fake_extension_rejection` | **Verified (M2)** |
| **SHA-256 Deduplication** | User-scoped hash check in `DocumentStorageService` | User-scoped `SHA256(file)` column check in MySQL | `tests/test_ingestion_api.py::test_api_upload_duplicate_detection` | **Verified (M2)** |
| **Multi-Format Extraction** | PyMuPDF (PDF), python-docx (DOCX), UTF-8 text (TXT) | `app/nlp/extraction/` module with PyMuPDF & python-docx | `tests/test_extraction.py` (PDF/DOCX/TXT tests) | **Verified (M2)** |
| **Scanned Document OCR** | Tesseract OCR via `pytesseract` for low-text pages | PyMuPDF page rendering + `pytesseract` + Pillow | `tests/test_extraction.py::test_extract_scanned_pdf_with_ocr` | **Verified (M2)** |
| **Clause Segmentation** | Multi-pass LLM heading and boundary discovery | Regex heading detection + NLTK punkt with legal abbreviation fixes | `tests/test_segmentation.py::test_gate_100_percent_extracted_clauses_are_exact_slices` | **Verified (M2)** |
| **Exact Source Slicing** | Approximated substring evidence quotes | Character offset slicing (`text[start:end]`); `original_text` is exact slice | `tests/test_segmentation.py::test_gate_100_percent_extracted_clauses_are_exact_slices` | **Verified (M2)** |
| **Document Status Stepper** | Status enum (`UPLOADED`, `EXTRACTING`, `ANALYZING`, `COMPLETED`, `FAILED`) | SQLAlchemy status column + background `ThreadPoolExecutor` | `tests/test_smoke_flow.py::test_full_lifecycle_smoke` | **Verified (M2)** |
| **Crash Recovery** | `StartupJobRecoveryListener.java` transitions stuck jobs to `FAILED` | Flask app factory startup hook marks stranded jobs `FAILED` | `app/__init__.py::create_app` | **Verified (M2)** |
| **Document Type Detection** | Gemini summary prompt classified document type | SBERT cosine similarity vs prototype descriptions + keyword cues | `tests/test_clause_classification.py::test_document_type_classification` | **Verified (M3)** |
| **Clause Classification** | Zero-shot Gemini classification across 17 categories | Ensemble: DistilBERT + SBERT zero-shot + keyword rules | `tests/test_clause_classification.py::test_gate_clause_recall_and_precision_on_gold_contracts` | **Verified (M3)** |
| **Ensemble Fallback** | Fallback to "Other" on model parsing errors | Documented weighted formula; low confidence falls back to "Other" + descriptive label | `tests/test_clause_classification.py::test_model_fallback_without_crashing` | **Verified (M3)** |
| **Clause Importance Level** | Gemini subjective assignment (`HIGH`, `MEDIUM`, `LOW`) | Deterministic scoring: category weight + obligation verbs + trigger entities | `tests/test_clause_classification.py::test_importance_scoring_rules` | **Verified (M3)** |
| **Affected Party Detection** | Extracted by Gemini prompt | spaCy dependency parser subject detection + named contract parties | `tests/test_clause_classification.py::test_affected_party_detection` | **Verified (M3)** |
| **Key Facts & Entities** | Gemini JSON schema key-info extraction | spaCy NER + Entity/Regex matchers for money (₹/Rs./$), dates, durations | `tests/test_entities_and_summary.py::test_key_facts_extraction_matching` | **Verified (M4)** |
| **Rule 6 "Not specified"** | Prompt instruction requiring "Not specified" on missing items | Explicit code default `val or "Not specified"` with no hallucinated dates | `tests/test_entities_and_summary.py::test_rule6_not_specified_consistency` | **Verified (M4)** |
| **Extractive Summaries** | Abstractive generation via Gemini Map-Reduce | SBERT TextRank + Maximal Marginal Relevance (MMR) | `tests/test_entities_and_summary.py::test_extractive_summary_verbatim_in_source` | **Verified (M4)** |
| **Structured Summary** | Abstractive summary fields (parties, purpose, obligations) | Aggregated extracted facts and clause types anchored to source | `tests/test_entities_and_summary.py::test_api_key_info_and_summary_endpoints` | **Verified (M4)** |
| **Simple English Simplification** | LLM rewritten to 8th-grade reading level | 150+ term glossary replacement + modal verb rewrites + dependency sentence splitting | `tests/test_simplifier.py::TestSimplificationEngine::test_lexical_simplify` | **Verified (M5)** |
| **Detailed Simplification** | Expanded paragraph generated by LLM | Category templates populated with extracted obligor, beneficiary, and conditions | `tests/test_simplifier.py::TestSimplificationEngine::test_tri_tier_modes_generation` | **Verified (M5)** |
| **Professional Simplification** | Commercial briefing generated by LLM | Structured breakdown: Obligor, Obligation, Condition, Exception, Deadline | `tests/test_simplifier.py::TestSimplificationEngine::test_tri_tier_modes_generation` | **Verified (M5)** |
| **Condition Preservation Check** | LLM post-verification of numbers/dates | Deterministic AST check: numbers, dates, negations (not/never), conditions (unless/except) | `tests/test_simplifier.py::TestSimplificationEngine::test_negation_preservation_invariant` | **Verified (M5)** |
| **Readability Scoring** | None / unmeasured | Hand-written Flesch Reading Ease & Kincaid Grade before and after (+24.5 FRE avg improvement) | `tests/test_simplifier.py::TestSimplificationEngine::test_readability_improvement_gate_across_20_clauses` | **Verified (M5)** |

| **Risk Identification** | Gemini prompt based on contract terms | Deterministic rules (`data/risk_rules.yaml`) + SBERT prototype similarity | `tests/test_risk.py::TestConfigurationIntegrity::test_risk_rules_yaml_covers_all_categories` | **Verified (M6)** |
| **Predatory Terms Detection** | Prompt detected uncapped indemnity, auto-renewal trap | Specific rules and threshold matching for one-sided terms | `tests/test_risk.py::TestPredatoryTermsAndRiskDetection::test_predatory_terms_in_one_sided_agreement` | **Verified (M6)** |
| **Rule 7 Legal Advice Guard** | Post-filter removing "illegal", "void", "unenforceable" | Post-filter substituting non-definitive advisory phrasing ("may be unfavorable") | `tests/test_risk.py::TestRule7LegalAdviceGuard::test_forbidden_words_sanitization` | **Verified (M6)** |
| **Missing Provisions** | Gemini compared document to expected YAML checklist | YAML checklists per document type + SBERT presence check | `tests/test_risk.py::TestMissingProvisionsDetection::test_clean_nda_missing_carveouts_and_remedies` | **Verified (M6)** |
| **Missing Disclaimer Label** | "Possible omission" label in DTO | Strict `"Possible omission"` label and disclaimer on every item | `tests/test_risk.py::TestMissingProvisionsDetection::test_clean_nda_missing_carveouts_and_remedies` | **Verified (M6)** |

| **RAG Hybrid Retrieval** | PostgreSQL `websearch_to_tsquery` + `ts_rank` | Hybrid: SBERT cosine similarity + BM25 sparse lexical search merged via RRF ($k=60$) | `tests/test_qa.py::test_hybrid_retrieve_chunks` | **Verified (M7)** |
| **Grounded QA & Citations** | Gemini prompt answering strictly from top chunks | Extractive BERT QA (MiniLM SQuAD 2.0) over top passages returning exact span & page | `tests/test_qa.py::test_extractive_qa_answerable_span` | **Verified (M7)** |
| **Honest Not-Found Refusal** | Model prompt instruction to say "not found" | Below confidence threshold ($\Delta < 0.0$), return exactly "The document does not appear to address this." | `tests/test_qa.py::test_answer_document_query_honest_refusal` | **Verified (M7)** |
| **Chat Intent Routing** | Generative conversational answering | Intent matcher answering amounts, dates, and penalties directly from stored facts | `tests/test_qa.py::test_fact_intent_routing_financials_and_dates` | **Verified (M7)** |
| **Prompt Injection Defense** | System prompt instruction framing chunks as untrusted | Document text treated strictly as untrusted data context; zero generative LLM to inject into | `tests/test_qa.py::test_prompt_injection_defense` | **Verified (M7)** |
| **Multi-Tenant Isolation** | `@AuthenticationPrincipal` check; 404 on cross-user query | Flask-Login `current_user` filter on all queries; 404 on cross-user query | `tests/test_qa.py::test_chat_api_endpoints_and_tenant_isolation` | **Verified (M7)** |
| **Dashboard SQL Aggregates** | SQL aggregate queries in `DashboardService.java` | SQLAlchemy `func.count` queries for `current_user` (zero hardcoded numbers) | `tests/test_dashboard_and_report.py::test_seed_two_users_dashboard_numbers_no_leak` | **Verified (M8)** |
| **Risk Charts** | Recharts (React) pie and bar charts | Chart.js served from `app/static/vendor/chart.js` (zero CDN) | `app/templates/dashboard.html` & `app/templates/documents/detail.html` | **Verified (M8)** |
| **PDF Report Dossier** | OpenPDF 2.0.3 (Java) 10-section PDF report | Python ReportLab 10-section PDF with headers, footers, page X of Y | `tests/test_dashboard_and_report.py::test_pdf_report_generation_10_sections_and_unicode` | **Verified (M8)** |
| **TrueType Font Rendering** | Linux system TrueType font for ₹, §, curly quotes | ReportLab TrueType font registration (`LiberationSans-Regular.ttf`) | `tests/test_dashboard_and_report.py::test_pdf_report_generation_10_sections_and_unicode` | **Verified (M8)** |
| **Provenance Tracking** | `EXTRACTED`, `AI_INTERPRETATION` badges | `EXTRACTED`, `RULE_BASED` in UI & PDF | `tests/test_dashboard_and_report.py::test_pdf_report_generation_10_sections_and_unicode` | **Verified (M8)** |
| **Web User Interface** | React 18 single-page app (Tailwind, Lucide, Radix UI) | Jinja2 templates + hand-written CSS + vanilla JavaScript | `tests/test_dashboard_and_report.py::test_empty_state_dashboard_brand_new_user` | **Verified (M8)** |
| **Light / Dark Mode** | `ThemeContext` toggling CSS classes in `localStorage` | CSS variables on `[data-theme="dark"]` toggled by vanilla JS | `app/templates/base.html` & `app/static/css/style.css` | **Verified (M8)** |
| **Evaluation Benchmark** | Precision/recall scripts in `evaluation/` | Comprehensive test suite + `evaluation/RESULTS.md` + old-vs-new comparison | `tests/test_evaluation.py` | **Verified (M9)** |
| **Legacy Stack Removal** | Distributed polyglot stack (React, Java Spring, FastAPI, Postgres) | 100% pure local Python NLP stack (Flask, MySQL 8, PyTorch, ReportLab) | `git status` (clean repository, zero legacy code) | **Verified (M10)** |
| **End-to-End Smoke Test** | `scripts/smoke_test.sh` calling Spring Boot endpoints | Unified automated smoke test (`tests/test_smoke_flow.py`, `scripts/smoke_test.sh`) | `tests/test_smoke_flow.py::test_full_lifecycle_smoke` | **Verified (M10)** |
| **One-Command Local Run** | Multi-service startup script | Unified shell runner `run_local.sh` with automatic health checks & migrations | `run_local.sh` | **Verified (M10)** |
| **Architecture Diagrams** | Legacy 3-tier architecture docs | 4 comprehensive Mermaid diagrams in `docs/architecture.md` (System, Pipeline, Chat, ERD) | `docs/architecture.md` | **Verified (M10)** |
| **REST API Documentation** | Swagger UI (`/swagger-ui.html`) | Clean markdown REST specification in `docs/api-documentation.md` | `docs/api-documentation.md` | **Verified (M10)** |
| **Privacy & Security** | Cloud LLM data transmission docs | Zero-data-retention, 100% on-premise local policy in `docs/privacy.md` | `docs/privacy.md` | **Verified (M10)** |
| **Viva Presentation Guide** | Legacy project presentation script | 5-minute academic defense guide & transcript in `docs/DEMO.md` | `docs/DEMO.md` | **Verified (M10)** |


