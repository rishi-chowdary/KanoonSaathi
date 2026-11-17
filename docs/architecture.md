# LexiLegal AI — System Architecture & Design Specification

## 1. System Overview

**LexiLegal AI** is an enterprise-grade legal document simplification and clause extraction platform engineered as a unified Python application. It operates entirely on-premise without external generative AI APIs, vector databases, or third-party cloud microservices.

### Target Technology Stack:
- **Application Framework**: Python 3.11+ / Flask (Application Factory, Blueprints, Flask-Login, Flask-WTF CSRF, Flask-Limiter)
- **Database Layer**: MySQL 8.0 (InnoDB, `utf8mb4` character set, Alembic migrations via Flask-Migrate)
- **Document Processing**: PyMuPDF (`fitz`), `python-docx`, Tesseract OCR (`pytesseract` + Pillow)
- **Machine Learning & NLP**: PyTorch, Hugging Face `transformers` (DistilBERT LEDGAR), `sentence-transformers` (`all-MiniLM-L6-v2`), spaCy (`en_core_web_md`), NLTK (Punkt tokenizer)
- **Extractive QA & Retrieval**: `deepset/minilm-uncased-squad2` + SBERT dense / BM25 sparse Reciprocal Rank Fusion (RRF)
- **Report Engine**: ReportLab 5 (10-Section Legal Dossier, running headers, two-pass `NumberedCanvas`, TrueType font support)
- **Frontend / Presentation**: Jinja2 semantic templates, hand-crafted responsive CSS, vanilla JavaScript, Chart.js (served locally, zero CDN)

---

## 2. High-Level Architecture Diagram

```mermaid
flowchart TD
    User["User Web Browser\n(Semantic HTML5, CSS Variables, Vanilla JS, Chart.js)"]
    
    subgraph FlaskApp ["LexiLegal AI — Flask Monolith (Port 5000)"]
        subgraph WebTier ["Presentation & Routing Layer"]
            AuthBP["auth_bp\n(Flask-Login Sessions, CSRF, Password Hashing)"]
            DocBP["documents_bp\n(Upload, List, Detail, REST APIs, PDF Downloads)"]
            StudioBP["studio_bp\n(Interactive Tri-Tier Simplification Studio)"]
            MainBP["main_bp\n(Dashboard, Real SQL Aggregation)"]
        end

        subgraph ServiceTier ["Service & Orchestration Layer"]
            DocSvc["Document Service\n(Validation, Magic Bytes, SHA-256 Hashing)"]
            ClauseSvc["Clause Service\n(Ensemble Classification & Quote Verification)"]
            AnalysisSvc["Analysis Service\n(Key Facts, Preamble Parties, Summaries)"]
            RiskSvc["Risk Service\n(Grounded Detection & Missing Provision Checklists)"]
            ChatSvc["Chat Service\n(Conversation Lifecycles & Grounded QA)"]
            ReportSvc["Report Service\n(ReportLab 10-Section Dossier Engine)"]
            DashboardSvc["Dashboard Service\n(Strict Tenant SQL Aggregation)"]
        end

        subgraph NLPTier ["Pure Python NLP Engine (Local In-Process)"]
            ExtractEng["Extraction & OCR Engine\n(PyMuPDF, python-docx, Tesseract)"]
            SegEng["Legal Segmentation Engine\n(Punkt Sentence Splitting & Regex Headings)"]
            ClassEng["Clause Classifier Ensemble\n(DistilBERT LEDGAR + SBERT + Keyword Rules)"]
            SummEng["Extractive Summarizer\n(SBERT TextRank + Maximal Marginal Relevance)"]
            SimpEng["Tri-Tier Simplifier\n(Glossary Substitution & Structural Decomposition)"]
            ReadEng["Readability Engine\n(Pure Python Flesch-Kincaid & Ease Formulas)"]
            RiskEng["Grounded Risk Engine\n(Rules, Regex, Thresholds + Rule 7 Guard)"]
            MissingEng["Missing Provisions Engine\n(Document-Type Checklists + SBERT Cosine)"]
            RetrievalEng["Hybrid Retrieval Engine\n(SBERT Dense + BM25 Sparse RRF k=60)"]
            QAEng["Extractive QA Engine\n(minilm-uncased-squad2 + Fact Intent Router)"]
            Registry["Model Registry\n(Single-point lazy loading & model caching)"]
        end
    end

    subgraph PersistenceTier ["Data Persistence & Storage"]
        MySQL[("MySQL 8.0 Database\n(InnoDB, utf8mb4, Indexes)")]
        FileStore[("Local Upload Storage\n(./uploads/<user_id>/)")]
    end

    User -->|HTTP / Session Cookie| WebTier
    WebTier --> ServiceTier
    ServiceTier --> NLPTier
    ServiceTier --> MySQL
    DocSvc --> FileStore
    NLPTier --> Registry
```

---

## 3. End-to-End Document Analysis Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant Flask as Flask Controller (documents_bp)
    participant DocSvc as Document Service
    participant NLPExt as Extraction & Segmentation
    participant NLPClass as Ensemble Classifier
    participant NLPRisk as Risk & Missing Engine
    participant DB as MySQL 8 (SQLAlchemy)
    
    User->>Flask: POST /api/documents/upload (Multipart PDF/DOCX/TXT)
    Flask->>DocSvc: save_and_extract_document(file_bytes, filename)
    DocSvc->>DocSvc: Validate magic bytes (%PDF, PK) & SHA-256 hash
    DocSvc->>NLPExt: extract_document() -> Pages, Sections, OCR
    DocSvc->>NLPExt: segment_clauses() & create_chunks()
    DocSvc->>DB: INSERT into documents & document_chunks
    DocSvc-->>Flask: Document (Status: UPLOADED)
    
    Flask->>DocSvc: Process Document Pipeline
    DocSvc->>NLPClass: classify_clause() & calculate_clause_importance()
    NLPClass->>NLPClass: DistilBERT LEDGAR + SBERT Prototype + Rules
    NLPClass->>DB: INSERT into extracted_clauses (100% Exact Quotes)
    
    DocSvc->>NLPRisk: detect_clause_risks() & detect_missing_provisions()
    NLPRisk->>NLPRisk: Apply risk_rules.yaml + Rule 7 Legal Guard
    NLPRisk->>DB: INSERT into risk_findings & missing_clause_warnings
    
    DocSvc->>DB: UPDATE documents (Status: COMPLETED, verification_rate: 100.0)
    DocSvc-->>Flask: Complete Analysis Bundle
    Flask-->>User: HTTP 201 Created (Redirect /documents/<id>)
```

---

## 4. Grounded Chat & Question Answering Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant ChatAPI as POST /api/documents/<id>/chat
    participant ChatSvc as Chat Service
    participant QAEng as QA & Intent Engine
    participant Retrieval as Hybrid Retrieval (SBERT + BM25)
    participant Model as deepset/minilm-uncased-squad2
    
    User->>ChatAPI: {"message": "How many days notice to prevent renewal?"}
    ChatAPI->>ChatSvc: send_chat_message(user_id, doc_id, query)
    ChatSvc->>QAEng: answer_document_query(query, analysis, chunks)
    
    rect rgb(240, 248, 255)
        Note over QAEng: 1. Fact Intent Router
        QAEng->>QAEng: Match regex intents (amount, dates, deadlines, parties)
    end
    
    rect rgb(255, 250, 240)
        Note over QAEng, Retrieval: 2. Hybrid Retrieval (if not resolved by metadata)
        QAEng->>Retrieval: hybrid_retrieve_chunks(query, chunks, top_k=4)
        Retrieval->>Retrieval: Dense Rank (SBERT) + Sparse Rank (BM25)
        Retrieval->>Retrieval: Reciprocal Rank Fusion (RRF, k=60)
        Retrieval-->>QAEng: Top-4 Attributed Chunks
    end
    
    rect rgb(245, 255, 250)
        Note over QAEng, Model: 3. Extractive QA & Honest Refusal
        QAEng->>Model: Forward pass over candidate chunk text
        Model-->>QAEng: start_logits, end_logits, null_score
        QAEng->>QAEng: Delta = best_span_score - null_score
        alt Delta >= 0.0 (Answerable)
            QAEng-->>ChatSvc: Extracted Span Text + Page Citation Badge
        else Delta < 0.0 (Unanswerable / Off-Topic)
            QAEng-->>ChatSvc: Honest Refusal ("The document does not appear to address this.")
        end
    end
    
    ChatSvc->>ChatSvc: Persist ChatConversation & ChatMessage to DB
    ChatSvc-->>ChatAPI: Response Payload
    ChatAPI-->>User: HTTP 200 OK {"answer": "...", "citations": [{"page": 1, ...}]}
```

---

## 5. Database Entity Relationship Diagram (ERD)

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
        datetime updated_at
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
        json main_conditions
        json obligations_summary
        json financial_terms_summary
        string llm_provider
        string llm_model
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
        integer clause_index
    }

    risk_findings {
        string id PK
        string analysis_id FK
        string rule_id
        string category
        string level
        string title
        text original_clause
        text explanation
        text why_it_matters
        text possible_consequences
        json suggested_questions
        integer source_page
        text evidence_quote
        boolean quote_verified
        string jurisdiction_caveat
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
        integer contract_amount_page
        string payment_deadlines
        integer payment_deadlines_page
        string penalties
        integer penalties_page
        string start_date
        integer start_date_page
        string end_date
        integer end_date_page
        string renewal_date
        integer renewal_date_page
        string notice_period
        integer notice_period_page
        string termination_conditions
        integer termination_conditions_page
        json obligations
        json important_dates
    }
```

---

## 6. Security & Guardrail Guarantees

1. **Deterministic Grounding**:
   - Zero generative LLM hallucinations.
   - 100% of quotes are exact substring slices verified against character offsets.
2. **Rule 7 Legal Advice Guard**:
   - Post-processor eliminates forbidden words (*"illegal"*, *"void"*, *"unenforceable"*, *"unlawful"*).
   - Missing provisions are tagged with strict non-definitive labels: `"Possible omission"`.
3. **Rule 6 Absent Field Invariant**:
   - Missing metadata fields strictly default to `"Not specified"`.
4. **Tenant Isolation**:
   - All queries filter strictly by `user_id == current_user.id`.
   - Access attempts to cross-user documents return HTTP 404 (preventing user ID enumeration).
5. **Session & Transport Protection**:
   - HTTP session cookies with `HttpOnly`, `SameSite=Lax`.
   - Form protection via Flask-WTF CSRF tokens on all web form submissions.
