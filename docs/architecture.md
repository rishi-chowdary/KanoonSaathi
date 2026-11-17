# System Architecture

KanoonSaathi is a single Flask application backed by MySQL 8 and a local Python NLP pipeline. All text extraction, classification, simplification, risk checks, and document Q&A run in-process without calling external AI services.

## Stack

- **Web server**: Python 3.11+, Flask (app factory, blueprints), Flask-Login, Flask-WTF (CSRF), Flask-Limiter
- **Database**: MySQL 8 (`InnoDB`, `utf8mb4`), SQLAlchemy, Alembic via Flask-Migrate
- **Extraction**: PyMuPDF (`fitz`), `python-docx`, Tesseract OCR (`pytesseract` + Pillow)
- **NLP and ML**: PyTorch, Hugging Face `transformers` (LEDGAR DistilBERT, `deepset/minilm-uncased-squad2`), `sentence-transformers` (`all-MiniLM-L6-v2`), spaCy (`en_core_web_md`), NLTK (`punkt`), scikit-learn
- **PDF reports**: ReportLab with local TrueType fonts (`LiberationSans`)
- **Frontend**: Jinja2 templates, hand-written CSS with local Liberation Serif fonts, vanilla JavaScript, local Chart.js (`app/static/vendor/chart.js`)

## Component overview

```mermaid
flowchart TD
    User["Web Browser (HTML, CSS, Vanilla JS, Chart.js)"]

    subgraph FlaskApp ["Flask Application (Port 5000)"]
        subgraph Routes ["Blueprints (app/blueprints/)"]
            AuthBP["auth (register, login, logout, profile)"]
            DocBP["documents (upload, list, detail, delete)"]
            AnalysisBP["analysis (clauses, risks, key info, status)"]
            ChatBP["chat (Q&A and conversations)"]
            ReportsBP["reports (PDF download and preview)"]
            StudioBP["studio (standalone clause simplifier)"]
            MainBP["main (landing page, dashboard)"]
        end

        subgraph Services ["Services (app/services/)"]
            DocSvc["document_service"]
            ClauseSvc["clause_service"]
            AnalysisSvc["analysis_service"]
            RiskSvc["risk_service"]
            ChatSvc["chat_service"]
            ReportSvc["report_service"]
            DashboardSvc["dashboard_service"]
        end

        subgraph NLP ["Local NLP Package (app/nlp/)"]
            Extract["extraction.py (PDF, DOCX, TXT, OCR)"]
            Segment["segmentation.py (headings + punkt)"]
            Classify["clause_classifier.py + document_classifier.py"]
            Summary["summarizer.py + key_info.py + parties.py"]
            Simplify["simplification/ (glossary, rewriter, templates, traps)"]
            Risk["risk_engine.py + missing_provisions.py"]
            QA["retrieval.py (SBERT + BM25 RRF) + qa_engine.py"]
            Registry["registry.py (lazy model singletons)"]
        end
    end

    MySQL[("MySQL 8 (10 tables)")]
    Uploads[("Local uploads (./uploads/<user_id>/)")]

    User --> Routes
    Routes --> Services
    Services --> NLP
    Services --> MySQL
    DocSvc --> Uploads
    NLP --> Registry
```

Routes stay thin: they validate request inputs, enforce document ownership (`app/blueprints/guards.py`), call a service function, and render HTML or JSON.

## Document ingestion and analysis flow

```mermaid
sequenceDiagram
    actor User
    participant Routes as documents blueprint
    participant DocSvc as document_service
    participant NLP as app/nlp/
    participant DB as MySQL 8

    User->>Routes: POST /documents/upload or /api/documents/upload
    Routes->>DocSvc: save_and_extract_document(file_bytes, filename)
    DocSvc->>DocSvc: Validate extension, magic bytes, size, SHA-256 duplicate
    DocSvc->>NLP: extract_document() -> pages and full text
    DocSvc->>NLP: create_chunks()
    DocSvc->>DB: Save Document and DocumentChunk rows
    DocSvc->>NLP: segment_clauses(), classify_clause(), simplify_clause()
    DocSvc->>DB: Save ExtractedClause rows (with exact source offsets)
    DocSvc->>NLP: extract_contract_key_info(), generate_extractive_summary()
    DocSvc->>DB: Save DocumentAnalysis and ExtractedInformation rows
    DocSvc->>NLP: detect_clause_risks(), detect_missing_provisions()
    DocSvc->>DB: Save RiskFinding and MissingClauseWarning rows
    DocSvc->>DB: Update Document status (COMPLETED or COMPLETED_WITH_WARNINGS)
    Routes-->>User: Redirect to /documents/<id> or return 201 JSON
```

On startup, `app/__init__.py` checks for documents left in `EXTRACTING` or `ANALYZING` from an interrupted run and marks them `FAILED` with a recovery reason.

## Document Q&A flow

```mermaid
sequenceDiagram
    actor User
    participant ChatAPI as chat blueprint
    participant ChatSvc as chat_service
    participant QA as qa_engine.py
    participant Retrieval as retrieval.py
    participant Model as minilm-uncased-squad2

    User->>ChatAPI: POST /api/documents/<id>/chat
    ChatAPI->>ChatSvc: send_chat_message(user_id, doc_id, query)
    ChatSvc->>QA: answer_document_query(query, analysis, chunks)
    QA->>QA: Check deterministic fact intents (amounts, dates, deadlines, parties)
    alt Matched stored key fact
        QA-->>ChatSvc: Fact answer with page citation
    else General document question
        QA->>Retrieval: hybrid_retrieve_chunks(query, chunks, top_k=4)
        Retrieval-->>QA: Top chunks via SBERT + BM25 RRF (k=60)
        QA->>Model: Score extractive answer span vs null score
        alt span_score - null_score >= 0.0
            QA-->>ChatSvc: Extracted span with page citation
        else Below threshold
            QA-->>ChatSvc: "The document does not appear to address this."
        end
    end
    ChatSvc->>ChatSvc: Persist ChatConversation and ChatMessage
    ChatAPI-->>User: 200 JSON with answer and citations
```

## Database schema

```mermaid
erDiagram
    users ||--o{ documents : owns
    users ||--o{ chat_conversations : creates
    documents ||--|| document_analyses : has
    documents ||--o{ document_chunks : contains
    documents ||--o{ chat_conversations : relates_to
    chat_conversations ||--o{ chat_messages : contains
    document_analyses ||--o{ extracted_clauses : contains
    document_analyses ||--o{ risk_findings : contains
    document_analyses ||--o{ missing_clause_warnings : contains
    document_analyses ||--|| extracted_information : stores

    users {
        string id PK
        string email UK
        string password_hash
        string full_name
        string role
        datetime created_at
    }

    documents {
        string id PK
        string user_id FK
        string original_filename
        string storage_path
        string file_type
        integer file_size
        string file_hash
        integer page_count
        string status
        string failure_reason
        datetime created_at
    }

    document_chunks {
        string id PK
        string document_id FK
        integer chunk_index
        integer page_number
        text content
        integer token_count
    }

    document_analyses {
        string id PK
        string document_id FK
        string title
        string document_type
        text purpose
        json parties
        text summary_short
        text summary_detailed
        float verification_rate
    }

    extracted_clauses {
        string id PK
        string analysis_id FK
        string title
        string category
        string section_reference
        text original_text
        text simplified_simple
        text simplified_detailed
        text simplified_professional
        string importance
        text evidence_quote
        boolean quote_verified
        integer source_page
    }

    risk_findings {
        string id PK
        string analysis_id FK
        string rule_id
        string category
        string level
        string title
        text explanation
        text why_it_matters
        text possible_consequences
        json suggested_questions
        integer source_page
        text evidence_quote
        boolean quote_verified
    }

    missing_clause_warnings {
        string id PK
        string analysis_id FK
        string clause_name
        string risk_level
        text why_it_matters
        text typical_provision
        string label
    }

    extracted_information {
        string id PK
        string analysis_id FK
        string contract_amount
        string payment_deadlines
        string penalties
        string start_date
        string end_date
        string renewal_date
        string notice_period
        string termination_conditions
        json obligations
        json important_dates
    }
```

## Design constraints and trade-offs

- **Source offset verification**: Every clause and evidence quote is checked as a slice of the extracted text (`quote_verified`). This prevents fabricated quotes, though it does not guarantee that a predicted category or risk rule is always right.
- **Non-definitive wording**: `soften_legal_claims()` in `app/nlp/risk_engine.py` replaces absolute terms ("illegal", "void", "unenforceable", "unlawful") with cautious phrasing, and absent metadata fields default to `"Not specified"`.
- **Rule-based simplification**: Simplification uses `data/glossary.yaml`, clause templates, and sentence splitting (`app/nlp/simplification/`) instead of a generative LLM. It preserves numbers, dates, and negations reliably, at the cost of less natural phrasing than a large language model.
- **Model domain and format limits**: The LEDGAR DistilBERT weights come from US SEC filings, DOCX page numbers are approximate character-count estimates, and all NLP rules target English text only.
- **User isolation**: Every document query filters by `current_user.id` and returns `404` when a document belongs to another account.
