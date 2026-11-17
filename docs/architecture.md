# LexiLegal AI — System Architecture & Design Specification

## 1. System Overview

LexiLegal AI is an enterprise-grade legal document analysis and simplification platform. It transforms complex legal contracts (leases, NDAs, vendor agreements, employment contracts) into plain-language summaries, structured clause inventories, grounded risk assessments, and verifiable citations.

### High-Level Architecture

```mermaid
flowchart TD
    Client["Client Web Browser\n(React 18 + Vite + Tailwind CSS)"]
    
    subgraph SpringBootApp ["Spring Boot Backend (Port 8080)"]
        Security["Security Filter Chain\n(JWT Auth + Rate Limiting)"]
        DocController["Document / Chat / Dashboard Controllers"]
        DocStorage["Local Storage Service\n(SHA-256 Deduplication & Magic Bytes)"]
        AsyncPipe["DocumentAsyncPipeline\n(Thread Pool Executor)"]
        ReportSvc["ReportPdfService\n(OpenPDF 2.0.3 Dossier Engine)"]
        ChatSvc["ChatService\n(PostgreSQL Full-Text Search RAG)"]
    end

    subgraph FastApiApp ["AI Engine Service (Port 8000)"]
        Extractor["PyMuPDF Document Extractor\n(Layout-aware Parser + OCR)"]
        Chunker["Sliding-Window Chunker\n(500-token chunks with overlap)"]
        SummaryAnalyzer["Summary & Conditions Analyzer"]
        ClauseAnalyzer["Clause Analyzer & Tri-Tier Simplifier"]
        RiskAnalyzer["Risk & Predatory Terms Analyzer"]
        KeyInfoAnalyzer["Key Info & Dates Extractor"]
        MissingAnalyzer["Missing Provisions Analyzer"]
        ChatEngine["Grounded RAG Chat Engine"]
        Rule7Filter["Rule 7 Post-Filter\n(Forbidden Phrase Redactor)"]
        QuoteVerifier["Quote Verifier\n(Exact + Fuzzy Levenshtein)"]
    end

    subgraph DataLayer ["Data Persistence Layer"]
        SupabasePostgres[("PostgreSQL Database\n(Supabase Cloud Pooler)")]
        FileStore[("File Storage\n(./uploads filesystem)")]
    end

    subgraph ExternalLLM ["LLM Inference Providers"]
        GeminiAPI["Google Gemini API\n(gemini-3.5-flash-lite)"]
        MockLLM["Mock Deterministic Provider\n(Zero-token offline tests)"]
    end

    Client -->|HTTPS / REST| Security
    Security --> DocController
    DocController --> DocStorage
    DocController --> ChatSvc
    DocController --> ReportSvc
    DocStorage --> FileStore
    DocController --> AsyncPipe
    
    ChatSvc -->|Full-Text Search ts_rank| SupabasePostgres
    ChatSvc -->|Grounding Context| ChatEngine
    
    AsyncPipe -->|Internal REST X-Internal-Api-Key| FastApiApp
    AsyncPipe -->|Entities & Chunks| SupabasePostgres
    
    Extractor --> Chunker
    Chunker --> FastApiApp
    
    SummaryAnalyzer --> ExternalLLM
    ClauseAnalyzer --> ExternalLLM
    RiskAnalyzer --> ExternalLLM
    KeyInfoAnalyzer --> ExternalLLM
    MissingAnalyzer --> ExternalLLM
    ChatEngine --> ExternalLLM
    
    RiskAnalyzer --> Rule7Filter
    ClauseAnalyzer --> QuoteVerifier
```

---

## 2. Multi-Stage Asynchronous Ingestion & Analysis Pipeline

When a user uploads a contract, the backend executes an asynchronous processing pipeline to avoid blocking HTTP requests while delivering real-time status updates.

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant Controller as DocumentController
    participant Storage as DocumentStorageService
    participant Pipeline as DocumentAsyncPipeline
    participant DB as PostgreSQL (Supabase)
    participant Engine as AI Engine (FastAPI)
    participant LLM as Google Gemini API

    User->>Controller: POST /api/documents/upload (Multipart PDF/DOCX)
    Controller->>Storage: validate(file) [Magic bytes, Size <= 10MB]
    Storage->>Storage: computeSha256(file)
    Controller->>DB: INSERT INTO documents (status='UPLOADED')
    Controller-->>User: 202 Accepted {id, status='UPLOADED'}
    
    Controller->>Pipeline: processDocumentAsync(docId)
    Pipeline->>DB: UPDATE documents SET status='EXTRACTING'
    Pipeline->>Engine: POST /internal/extract (Document file)
    Engine->>Engine: PyMuPDF page-by-page layout & text extraction
    Engine->>Engine: Semantic Chunking (500 tokens / 50 overlap)
    Engine-->>Pipeline: ExtractionResponseDto (pages, chunks)
    Pipeline->>DB: INSERT INTO document_chunks (page, content, tsv)
    Pipeline->>DB: UPDATE documents SET status='ANALYZING', page_count=N
    
    Note over Pipeline,Engine: Multi-Pass Map-Reduce Analysis
    Pipeline->>Engine: POST /internal/analyze/summary
    Engine->>LLM: Generate summary, purpose, parties, obligations
    Engine-->>Pipeline: DocumentSummaryResponseDto
    Pipeline->>DB: INSERT INTO document_analyses
    
    Pipeline->>Engine: POST /internal/analyze/clauses
    Engine->>LLM: Extract clauses & generate 3 simplification tiers
    Engine->>Engine: verify_quote(quote, pages)
    Engine-->>Pipeline: ClauseAnalysisResponseDto
    Pipeline->>DB: INSERT INTO extracted_clauses
    
    Pipeline->>Engine: POST /internal/analyze/risks
    Engine->>LLM: Detect high/medium/low risks & predatory traps
    Engine->>Engine: filter_rule7_language() [Redact "illegal", "void"]
    Engine-->>Pipeline: RiskAnalysisResponseDto
    Pipeline->>DB: INSERT INTO risk_findings
    
    Pipeline->>Engine: POST /internal/analyze/key-info
    Engine->>LLM: Extract payment deadlines, dates, amounts
    Engine-->>Pipeline: KeyInfoResponseDto
    Pipeline->>DB: INSERT INTO extracted_information
    
    Pipeline->>Engine: POST /internal/analyze/missing
    Engine->>LLM: Compare vs. expected provisions checklist
    Engine-->>Pipeline: MissingProvisionsResponseDto
    Pipeline->>DB: INSERT INTO missing_clause_warnings
    
    Pipeline->>DB: UPDATE documents SET status='COMPLETED'
    User->>Controller: GET /api/documents/{id}/status (Polling)
    Controller-->>User: {status: 'COMPLETED'}
```

---

## 3. Grounded Retrieval-Augmented Generation (RAG) Document Chat

The document chat facility strictly refuses to invent legal clauses or follow instructions contained within document text.

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant ChatCtrl as ChatController
    participant ChatSvc as ChatService
    participant DB as PostgreSQL (Supabase)
    participant Engine as AI Engine (FastAPI)
    participant LLM as Google Gemini API

    User->>ChatCtrl: POST /api/documents/{id}/chat {message}
    ChatCtrl->>ChatSvc: sendMessage(userId, docId, message)
    ChatSvc->>DB: Verify document ownership (tenant isolation)
    
    ChatSvc->>DB: Full-Text Search ts_rank(tsv, websearch_to_tsquery(:query))
    alt Full-Text Matches Found
        DB-->>ChatSvc: Top-5 relevant chunks with page attribution
    else No FTS Match
        ChatSvc->>DB: Fallback: Token-broadened query / chronological chunks
        DB-->>ChatSvc: Candidate chunks
    end
    
    ChatSvc->>DB: Load last 6 messages from chat_messages
    ChatSvc->>Engine: POST /internal/chat {question, chunks, history}
    Note over Engine: Untrusted Data Framing:\nTreat chunk text as untrusted data.\nReject prompt injection attacks.
    Engine->>LLM: Generate grounded answer strictly from chunks
    LLM-->>Engine: RawChatResult {answer, citations: [{page, quote}], confidence}
    Engine->>Engine: verify_quote(quote, chunks)
    Engine-->>ChatSvc: ChatResponseDto {answer, citations, confidence}
    
    ChatSvc->>DB: INSERT INTO chat_messages (user, assistant, citations)
    ChatSvc-->>ChatCtrl: ChatMessageResponse
    ChatCtrl-->>User: 200 OK {messageId, answer, citations, confidence}
```

---

## 4. Key Design Principles & Safeguards

1. **Rule 7 Compliance (Strict Advisory Framing)**:
   - The platform never outputs legal conclusions claiming a contract term is *"illegal"*, *"void"*, or *"unenforceable"*.
   - A deterministic post-processor sanitizes every response before persistence, substituting advisory phrasing such as *"may be subject to statutory challenge"* or *"presents significant enforceability risk"*.

2. **Rule 6 Grounding Safeguards**:
   - Absent provisions default strictly to `"Not specified"`. The model is prohibited from guessing payment schedules or durations when they are not present in the text.

3. **Multi-Tenant Isolation**:
   - Every database query filters by `user_id`. Any cross-tenant access attempt strictly returns `404 Not Found` (never `403 Forbidden`) to prevent document ID enumeration.

4. **Fault Tolerance & Reliability**:
   - AI Engine calls are wrapped in an exponential backoff retry loop (`executeWithRetry`) handling transient timeouts.
   - If secondary analyzers (e.g. key dates or missing provisions) experience unexpected failures while clauses succeed, the document transitions to `COMPLETED_WITH_WARNINGS` rather than aborting.
   - On backend restart, `StartupJobRecoveryListener` automatically scans for stranded `ANALYZING` jobs and marks them `FAILED` with an actionable user prompt to retry.
