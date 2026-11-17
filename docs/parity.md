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
| **Document Status Stepper** | Status enum (`UPLOADED`, `EXTRACTING`, `ANALYZING`, `COMPLETED`, `FAILED`) | SQLAlchemy status column + background `ThreadPoolExecutor` | `tests/test_jobs.py::test_async_job_lifecycle` | Planned (M2) |
| **Crash Recovery** | `StartupJobRecoveryListener.java` transitions stuck jobs to `FAILED` | Flask app factory startup hook marks stranded jobs `FAILED` | `tests/test_jobs.py::test_startup_recovery_of_stuck_jobs` | Planned (M2) |
| **Document Type Detection** | Gemini summary prompt classified document type | SBERT cosine similarity vs prototype descriptions + keyword cues | `tests/test_clause_classification.py::test_document_type_classification` | **Verified (M3)** |
| **Clause Classification** | Zero-shot Gemini classification across 17 categories | Ensemble: DistilBERT + SBERT zero-shot + keyword rules | `tests/test_clause_classification.py::test_gate_clause_recall_and_precision_on_gold_contracts` | **Verified (M3)** |
| **Ensemble Fallback** | Fallback to "Other" on model parsing errors | Documented weighted formula; low confidence falls back to "Other" + descriptive label | `tests/test_clause_classification.py::test_model_fallback_without_crashing` | **Verified (M3)** |
| **Clause Importance Level** | Gemini subjective assignment (`HIGH`, `MEDIUM`, `LOW`) | Deterministic scoring: category weight + obligation verbs + trigger entities | `tests/test_clause_classification.py::test_importance_scoring_rules` | **Verified (M3)** |
| **Affected Party Detection** | Extracted by Gemini prompt | spaCy dependency parser subject detection + named contract parties | `tests/test_clause_classification.py::test_affected_party_detection` | **Verified (M3)** |
| **Key Facts & Entities** | Gemini JSON schema key-info extraction | spaCy NER + EntityRuler for money (₹/Rs./$), dates, durations | `tests/test_entities.py::test_key_facts_extraction` | Planned (M4) |
| **Rule 6 "Not specified"** | Prompt instruction requiring "Not specified" on missing items | Explicit code default `val or "Not specified"` with no hallucinated dates | `tests/test_entities.py::test_rule6_not_specified_consistency` | Planned (M4) |
| **Extractive Summaries** | Abstractive generation via Gemini Map-Reduce | SBERT TextRank + Maximal Marginal Relevance (MMR) | `tests/test_summarizer.py::test_summary_sentences_verbatim_in_source` | Planned (M4) |
| **Structured Summary** | Abstractive summary fields (parties, purpose, obligations) | Aggregated extracted facts and clause types anchored to source | `tests/test_summarizer.py::test_structured_summary_anchoring` | Planned (M4) |
| **Simple English Simplification** | LLM rewritten to 8th-grade reading level | 150+ term glossary replacement + modal verb rewrites + dependency sentence splitting | `tests/test_simplifier.py::test_simple_english_glossary_substitutions` | Planned (M5) |
| **Detailed Simplification** | Expanded paragraph generated by LLM | Category templates populated with extracted obligor, beneficiary, and conditions | `tests/test_simplifier.py::test_detailed_template_population` | Planned (M5) |
| **Professional Simplification** | Commercial briefing generated by LLM | Structured breakdown: Obligor, Obligation, Condition, Exception, Deadline | `tests/test_simplifier.py::test_professional_structured_breakdown` | Planned (M5) |
| **Condition Preservation Check** | LLM post-verification of numbers/dates | Deterministic AST check: numbers, dates, negations (not/never), conditions (unless/except) | `tests/test_simplifier.py::test_preservation_fallback_on_drop` | Planned (M5) |
| **Readability Scoring** | None / unmeasured | Hand-written Flesch Reading Ease & Kincaid Grade before and after | `tests/test_simplifier.py::test_flesch_reading_ease_improvement` | Planned (M5) |
| **Risk Identification** | Gemini prompt based on contract terms | Deterministic rules (`data/risk_rules.yaml`) + SBERT prototype similarity | `tests/test_risk.py::test_risk_rule_coverage_and_thresholds` | Planned (M5) |
| **Predatory Terms Detection** | Prompt detected uncapped indemnity, auto-renewal trap | Specific rules and threshold matching for one-sided terms | `tests/test_risk.py::test_predatory_one_sided_agreement_risks` | Planned (M6) |
| **Rule 7 Legal Advice Guard** | Post-filter removing "illegal", "void", "unenforceable" | Post-filter substituting non-definitive advisory phrasing ("may be unfavorable") | `tests/test_risk.py::test_rule7_forbidden_words_zero` | Planned (M6) |
| **Missing Provisions** | Gemini compared document to expected YAML checklist | YAML checklists per document type + SBERT presence check | `tests/test_missing.py::test_missing_provisions_checklist_matching` | Planned (M6) |
| **Missing Disclaimer Label** | "Possible omission" label in DTO | Strict `"Possible omission"` label and disclaimer on every item | `tests/test_missing.py::test_possible_omission_label` | Planned (M6) |
| **RAG Hybrid Retrieval** | PostgreSQL `websearch_to_tsquery` + `ts_rank` | Hybrid: SBERT cosine similarity + MySQL FULLTEXT merged via RRF | `tests/test_retrieval.py::test_hybrid_retrieval_rrf` | Planned (M7) |
| **Grounded QA & Citations** | Gemini prompt answering strictly from top chunks | Extractive BERT QA (SQuAD 2.0) over top passages returning exact span & page | `tests/test_qa.py::test_grounded_qa_citations` | Planned (M7) |
| **Honest Not-Found Refusal** | Model prompt instruction to say "not found" | Below confidence threshold, return exactly "The document does not appear to address this." | `tests/test_qa.py::test_unanswerable_question_not_found` | Planned (M7) |
| **Chat Intent Routing** | Generative conversational answering | Intent matcher answering amounts, dates, and penalties directly from stored facts | `tests/test_qa.py::test_chat_intent_routing_facts` | Planned (M7) |
| **Prompt Injection Defense** | System prompt instruction framing chunks as untrusted | Text escaping in templates; zero generative LLM to inject into | `tests/test_security.py::test_injection_payload_escaped` | Planned (M7) |
| **Multi-Tenant Isolation** | `@AuthenticationPrincipal` check; 404 on cross-user query | Flask-Login `current_user` filter on all queries; 404 on cross-user query | `tests/test_security.py::test_tenant_isolation_404` | Planned (M8) |
| **Dashboard SQL Aggregates** | SQL aggregate queries in `DashboardService.java` | SQLAlchemy `func.count` queries for `current_user` (zero hardcoded numbers) | `tests/test_dashboard.py::test_dashboard_stats_match_sql` | Planned (M8) |
| **Risk Charts** | Recharts (React) pie and bar charts | Chart.js served from `app/static/vendor/chart.js` (zero CDN) | `tests/test_dashboard.py::test_chart_data_serialization` | Planned (M8) |
| **PDF Report Dossier** | OpenPDF 2.0.3 (Java) 10-section PDF report | Python ReportLab 10-section PDF with headers, footers, page X of Y | `tests/test_report.py::test_reportlab_10_sections_and_unicode` | Planned (M8) |
| **TrueType Font Rendering** | Linux system TrueType font for ₹, §, curly quotes | ReportLab TrueType font registration (`NotoSans-Regular.ttf`) | `tests/test_report.py::test_unicode_currency_and_symbols` | Planned (M8) |
| **Provenance Tracking** | `EXTRACTED`, `AI_INTERPRETATION` badges | `EXTRACTED`, `MODEL_PREDICTION`, `RULE_BASED` in UI & PDF | `tests/test_clauses.py::test_provenance_markers_serialized` | Planned (M8) |
| **Web User Interface** | React 18 single-page app (Tailwind, Lucide, Radix UI) | Jinja2 templates + hand-written CSS + vanilla JavaScript | Browser verification & `tests/test_ui.py` | Planned (M8) |
| **Light / Dark Mode** | `ThemeContext` toggling CSS classes in `localStorage` | CSS variables on `[data-theme="dark"]` toggled by vanilla JS | `tests/test_ui.py::test_theme_toggle_persistence` | Planned (M8) |
| **Evaluation Benchmark** | Precision/recall scripts in `evaluation/` | Comprehensive test suite + `evaluation/RESULTS.md` + old-vs-new comparison | `tests/test_evaluation.py` | Planned (M9) |

