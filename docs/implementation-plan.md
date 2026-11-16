# LexiLegal AI — Implementation Plan

This document details the engineering specifications, directory layout, database schema, API contracts, JSON schemas, state machine, and risk mitigations for the LexiLegal AI system.

---

## 1. Directory Structure

```
lexilegal-ai/
├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── .gitignore
├── .env.example
├── docs/
│   ├── implementation-plan.md
│   ├── PROGRESS.md
│   ├── architecture.md
│   ├── api-documentation.md
│   ├── privacy.md
│   └── viva/
│       ├── questions-and-answers.md
│       └── demo-script.md
├── postman/
│   ├── lexilegal.postman_collection.json
│   └── lexilegal.postman_environment.json
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── components/
│       │   ├── ui/
│       │   ├── common/
│       │   │   ├── Navbar.jsx
│       │   │   ├── Footer.jsx
│       │   │   ├── ProtectedRoute.jsx
│       │   │   ├── ProvenanceBadge.jsx
│       │   │   ├── PrivacyConsentModal.jsx
│       │   │   └── DuplicateFileModal.jsx
│       │   ├── analysis/
│       │   │   ├── SummaryTab.jsx
│       │   │   ├── ClausesTab.jsx
│       │   │   ├── RisksTab.jsx
│       │   │   ├── KeyInfoTab.jsx
│       │   │   ├── MissingClausesTab.jsx
│       │   │   └── DocumentViewer.jsx
│       │   └── chat/
│       │       ├── ChatWindow.jsx
│       │       └── CitationPill.jsx
│       ├── pages/
│       │   ├── LandingPage.jsx
│       │   ├── LoginPage.jsx
│       │   ├── RegisterPage.jsx
│       │   ├── DashboardPage.jsx
│       │   ├── UploadPage.jsx
│       │   ├── AnalysisPage.jsx
│       │   ├── HistoryPage.jsx
│       │   └── ProfilePage.jsx
│       ├── layouts/
│       │   ├── AppLayout.jsx
│       │   └── AuthLayout.jsx
│       ├── services/
│       │   ├── api.js
│       │   ├── authService.js
│       │   ├── documentService.js
│       │   └── chatService.js
│       ├── hooks/
│       │   ├── useAuth.js
│       │   ├── useTheme.js
│       │   └── useDocumentPolling.js
│       ├── context/
│       │   ├── AuthContext.jsx
│       │   └── ThemeContext.jsx
│       └── utils/
│           ├── formatters.js
│           └── constants.js
├── backend/
│   ├── pom.xml
│   └── src/
│       ├── main/
│       │   ├── java/com/lexilegal/
│       │   │   ├── LexiLegalApplication.java
│       │   │   ├── config/
│       │   │   │   ├── AsyncConfig.java
│       │   │   │   ├── CorsConfig.java
│       │   │   │   ├── OpenApiConfig.java
│       │   │   │   ├── RateLimitConfig.java
│       │   │   │   ├── SecurityConfig.java
│       │   │   │   ├── StorageConfig.java
│       │   │   │   └── WebClientConfig.java
│       │   │   ├── controller/
│       │   │   │   ├── AuthController.java
│       │   │   │   ├── DocumentController.java
│       │   │   │   ├── AnalysisController.java
│       │   │   │   ├── ChatController.java
│       │   │   │   ├── ReportController.java
│       │   │   │   └── DashboardController.java
│       │   │   ├── dto/
│       │   │   │   ├── request/
│       │   │   │   │   ├── LoginRequest.java
│       │   │   │   │   ├── RegisterRequest.java
│       │   │   │   │   ├── UpdateProfileRequest.java
│       │   │   │   │   ├── ChatMessageRequest.java
│       │   │   │   │   └── UploadOptionsRequest.java
│       │   │   │   └── response/
│       │   │   │       ├── AuthResponse.java
│       │   │   │       ├── UserProfileResponse.java
│       │   │   │       ├── DocumentResponse.java
│       │   │   │       ├── DocumentStatusResponse.java
│       │   │   │       ├── DocumentTextResponse.java
│       │   │   │       ├── DuplicateCheckResponse.java
│       │   │   │       ├── AnalysisSummaryResponse.java
│       │   │   │       ├── ClauseResponse.java
│       │   │   │       ├── RiskResponse.java
│       │   │   │       ├── KeyInfoResponse.java
│       │   │   │       ├── MissingClauseResponse.java
│       │   │   │       ├── ChatResponse.java
│       │   │   │       ├── DashboardStatsResponse.java
│       │   │   │       └── ErrorResponse.java
│       │   │   ├── entity/
│       │   │   │   ├── User.java
│       │   │   │   ├── Document.java
│       │   │   │   ├── DocumentAnalysis.java
│       │   │   │   ├── ExtractedClause.java
│       │   │   │   ├── RiskFinding.java
│       │   │   │   ├── ExtractedInformation.java
│       │   │   │   ├── MissingClauseWarning.java
│       │   │   │   ├── DocumentChunk.java
│       │   │   │   ├── ChatConversation.java
│       │   │   │   └── ChatMessage.java
│       │   │   ├── exception/
│       │   │   │   ├── GlobalExceptionHandler.java
│       │   │   │   ├── ResourceNotFoundException.java
│       │   │   │   ├── InvalidFileException.java
│       │   │   │   ├── DuplicateDocumentException.java
│       │   │   │   ├── RateLimitExceededException.java
│       │   │   │   └── AiEngineException.java
│       │   │   ├── repository/
│       │   │   │   ├── UserRepository.java
│       │   │   │   ├── DocumentRepository.java
│       │   │   │   ├── DocumentAnalysisRepository.java
│       │   │   │   ├── ExtractedClauseRepository.java
│       │   │   │   ├── RiskFindingRepository.java
│       │   │   │   ├── ExtractedInformationRepository.java
│       │   │   │   ├── MissingClauseWarningRepository.java
│       │   │   │   ├── DocumentChunkRepository.java
│       │   │   │   ├── ChatConversationRepository.java
│       │   │   │   └── ChatMessageRepository.java
│       │   │   ├── security/
│       │   │   │   ├── JwtTokenProvider.java
│       │   │   │   ├── JwtAuthFilter.java
│       │   │   │   ├── RateLimitingFilter.java
│       │   │   │   ├── CustomUserDetailsService.java
│       │   │   │   └── UserPrincipal.java
│       │   │   └── service/
│       │   │       ├── AuthService.java
│       │   │       ├── DocumentService.java
│       │   │       ├── AnalysisAsyncService.java
│       │   │       ├── ChunkRetrievalService.java
│       │   │       ├── ReportService.java
│       │   │       ├── DashboardService.java
│       │   │       └── client/
│       │   │           └── AiEngineClient.java
│       │   └── resources/
│       │       ├── application.yml
│       │       └── db/migration/
│       │           ├── V1__init_schema.sql
│       │           └── V2__add_indexes.sql
│       └── test/
│           └── java/com/lexilegal/
│               ├── controller/
│               ├── service/
│               └── security/
├── ai-engine/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── routes.py
│   │   ├── extractors/
│   │   │   ├── pdf_extractor.py
│   │   │   ├── docx_extractor.py
│   │   │   ├── txt_extractor.py
│   │   │   └── ocr_extractor.py
│   │   ├── services/
│   │   │   ├── text_chunker.py
│   │   │   ├── quote_verifier.py
│   │   │   └── llm_service.py
│   │   ├── providers/
│   │   │   ├── base.py
│   │   │   ├── gemini_provider.py
│   │   │   └── ollama_provider.py
│   │   ├── analyzers/
│   │   │   ├── summarizer.py
│   │   │   ├── clause_analyzer.py
│   │   │   ├── risk_analyzer.py
│   │   │   ├── key_info_analyzer.py
│   │   │   ├── missing_clause_detector.py
│   │   │   └── chat_rag.py
│   │   ├── prompts/
│   │   │   ├── system_prompts.py
│   │   │   └── analysis_prompts.py
│   │   ├── schemas/
│   │   │   ├── extraction.py
│   │   │   ├── summary.py
│   │   │   ├── clause.py
│   │   │   ├── risk.py
│   │   │   ├── key_info.py
│   │   │   ├── missing_clause.py
│   │   │   └── chat.py
│   │   └── utils/
│   │       └── text_utils.py
│   └── tests/
│       ├── conftest.py
│       ├── test_extractors.py
│       ├── test_quote_verifier.py
│       ├── test_schemas.py
│       └── test_injection_defense.py
├── samples/
│   ├── contracts/
│   │   ├── non_disclosure_agreement.pdf
│   │   ├── commercial_lease_agreement.pdf
│   │   ├── software_services_contract.docx
│   │   ├── employment_agreement.txt
│   │   └── prompt_injection_test.txt
│   └── gold/
│       ├── nda_expected.json
│       ├── lease_expected.json
│       └── service_expected.json
└── evaluation/
    ├── evaluate.py
    ├── metrics.py
    └── results/
```

---

## 2. API Endpoint List

### 2.1 Backend Endpoints (Spring Boot)

All authenticated endpoints require an `Authorization: Bearer <JWT>` header. Per-user data isolation is enforced on every access: accessing a resource belonging to another user returns HTTP 404 (not 403) to prevent ID enumeration.

| Method | Path | Auth Rule | Request Body / Params | Response | Description |
|---|---|---|---|---|---|
| `POST` | `/api/auth/register` | None (Public, Rate-Limited: 5 req/min) | `{ "email": "user@example.com", "password": "...", "fullName": "Alice" }` | 201 Created: `{ "token": "...", "user": { "id": "uuid", "email": "...", "fullName": "..." } }` | Register a new user |
| `POST` | `/api/auth/login` | None (Public, Rate-Limited: 5 req/min) | `{ "email": "user@example.com", "password": "..." }` | 200 OK: `{ "token": "...", "user": { "id": "uuid", "email": "...", "fullName": "..." } }` | Authenticate and obtain JWT |
| `POST` | `/api/auth/logout` | Bearer JWT (User) | None | 200 OK: `{ "message": "Logged out successfully" }` | Invalidate client session state |
| `GET` | `/api/auth/me` | Bearer JWT (User) | None | 200 OK: `{ "id": "uuid", "email": "...", "fullName": "...", "createdAt": "..." }` | Get current user profile |
| `PUT` | `/api/auth/profile` | Bearer JWT (User) | `{ "fullName": "Alice Smith", "password": "...?" }` | 200 OK: `{ "id": "uuid", "email": "...", "fullName": "..." }` | Update user profile name/password |
| `POST` | `/api/documents/upload` | Bearer JWT (User) | `multipart/form-data`: `file`, optional `reuseExisting: boolean`, `forceReanalyze: boolean` | 202 Accepted: `{ "id": "uuid", "originalFilename": "...", "fileSize": 12345, "status": "UPLOADED", "isDuplicate": false, "existingAnalysisId": null }` or 409 Conflict: `{ "isDuplicate": true, "existingDocumentId": "uuid", "existingAnalysisId": "uuid", "uploadedAt": "..." }` | Upload contract file (max 10MB). If SHA-256 matches existing document and `forceReanalyze` is false, offers reuse |
| `GET` | `/api/documents` | Bearer JWT (User) | Query: `page=0`, `size=10`, `search=`, `status=` | 200 OK: `{ "content": [ ... ], "totalElements": 25, "page": 0, "size": 10 }` | List user documents with pagination and filter |
| `GET` | `/api/documents/{id}` | Bearer JWT (User) | None | 200 OK: `{ "id": "uuid", "originalFilename": "...", "fileType": "PDF", "fileSize": 12345, "status": "COMPLETED", "failureReason": null, "pageCount": 4, "createdAt": "..." }` | Get single document metadata |
| `GET` | `/api/documents/{id}/status` | Bearer JWT (User) | None | 200 OK: `{ "id": "uuid", "status": "ANALYZING", "failureReason": null, "progressStep": "Extracting clauses", "updatedAt": "..." }` | Polling endpoint for upload progress (polled every 2.5s) |
| `GET` | `/api/documents/{id}/text` | Bearer JWT (User) | None | 200 OK: `{ "documentId": "uuid", "pages": [{ "pageNumber": 1, "text": "..." }] }` | Retrieve extracted page text for side-by-side document viewer |
| `DELETE` | `/api/documents/{id}` | Bearer JWT (User) | None | 204 No Content | Delete document, analysis, chunks, chat history, and storage file |
| `GET` | `/api/documents/{id}/analysis` | Bearer JWT (User) | None | 200 OK: Full analysis composite object (summary, clauses, risks, key_info, missing_clauses, metadata) | Complete document analysis overview |
| `GET` | `/api/documents/{id}/clauses` | Bearer JWT (User) | Query: `category=`, `importance=`, `search=` | 200 OK: `[ { "id": "uuid", "title": "...", "category": "Confidentiality", "originalText": "...", "simplifiedSimple": "...", "simplifiedDetailed": "...", "simplifiedProfessional": "...", "importance": "HIGH", "affectedParty": "Recipient", "sourcePage": 1, "sectionReference": "Section 3.1", "evidenceQuote": "...", "quoteVerified": true, "provenance": "EXTRACTED" } ]` | Extracted clauses with filters |
| `GET` | `/api/documents/{id}/risks` | Bearer JWT (User) | Query: `category=`, `level=` | 200 OK: `[ { "id": "uuid", "category": "LIABILITY", "level": "HIGH", "title": "Unlimited Indemnity", "originalClause": "...", "explanation": "...", "whyItMatters": "...", "possibleConsequences": "...", "suggestedQuestions": ["..."], "sourcePage": 2, "evidenceQuote": "...", "quoteVerified": true, "jurisdictionCaveat": "...", "provenance": "AI_INTERPRETATION" } ]` | Risk findings with category/level filters |
| `GET` | `/api/documents/{id}/key-info` | Bearer JWT (User) | None | 200 OK: `{ "contractAmount": "...", "contractAmountPage": 1, "paymentDeadlines": "...", "penalties": "...", "startDate": "...", "endDate": "...", "renewalDate": "...", "noticePeriod": "...", "terminationConditions": "...", "obligations": [...], "importantDates": [...] }` | Structured key commercial facts |
| `GET` | `/api/documents/{id}/missing-clauses` | Bearer JWT (User) | None | 200 OK: `[ { "id": "uuid", "category": "Dispute Resolution", "clauseName": "Arbitration Clause", "whyItMatters": "...", "typicalProvision": "...", "riskLevel": "MEDIUM", "label": "Possible omission" } ]` | Potential omitted provisions |
| `POST` | `/api/documents/{id}/chat` | Bearer JWT (User) | `{ "conversationId": "uuid?", "message": "What is the notice period?" }` | 200 OK: `{ "conversationId": "uuid", "messageId": "uuid", "answer": "...", "citations": [{ "chunkId": "uuid", "pageNumber": 2, "quote": "..." }], "addressedInDocument": true }` | Send question and get citation-grounded response |
| `GET` | `/api/documents/{id}/chat/history` | Bearer JWT (User) | Query: `conversationId=uuid?` | 200 OK: `{ "conversationId": "uuid", "messages": [{ "id": "uuid", "role": "USER", "content": "...", "citations": [], "createdAt": "..." }] }` | Retrieve conversation thread |
| `GET` | `/api/documents/{id}/report` | Bearer JWT (User) | None | 200 OK: `application/pdf` binary stream | Download generated 10-section PDF report |
| `GET` | `/api/dashboard/stats` | Bearer JWT (User) | None | 200 OK: `{ "totalDocuments": 12, "completedAnalyses": 11, "pendingAnalyses": 1, "failedAnalyses": 0, "totalClausesExtracted": 84, "riskDistribution": { "HIGH": 5, "MEDIUM": 14, "LOW": 20, "INFORMATIONAL": 8 }, "recentDocuments": [...] }` | Real database dashboard statistics |
| `GET` | `/swagger-ui.html` | None (Public) | None | 200 OK: HTML | Swagger UI interactive documentation |
| `GET` | `/v3/api-docs` | None (Public) | None | 200 OK: JSON | OpenAPI 3.0 specification |

---

### 2.2 Internal AI Engine Endpoints (FastAPI)

These endpoints bind only to `127.0.0.1` or the private Docker container network. They are never exposed to the browser or public internet. Requests from Spring Boot must carry the `X-Internal-Api-Key` header.

| Method | Path | Auth Rule | Request Body | Response | Description |
|---|---|---|---|---|---|
| `POST` | `/internal/extract` | Header: `X-Internal-Api-Key` | `multipart/form-data`: `file` | 200 OK: `{ "text": "...", "page_count": 4, "pages": [{ "page_number": 1, "text": "..." }], "is_scanned": false, "chunks": [{ "chunk_id": "...", "page_number": 1, "text": "...", "token_count": 280 }] }` | Parse file, apply OCR if scanned, chunk text with page metadata |
| `POST` | `/internal/analyze` | Header: `X-Internal-Api-Key` | `{ "document_id": "uuid", "pages": [{ "page_number": 1, "text": "..." }], "chunks": [...] }` | 200 OK: Full structured JSON (summary, clauses, risks, key_info, missing_clauses, verification metadata) | Execute map-reduce analysis and quote verification |
| `POST` | `/internal/chat` | Header: `X-Internal-Api-Key` | `{ "question": "...", "retrieved_chunks": [{ "chunk_id": "...", "page_number": 1, "text": "..." }], "conversation_history": [{ "role": "user", "content": "..." }] }` | 200 OK: `{ "answer": "...", "source_chunks": [{ "chunk_id": "...", "page_number": 1, "quote": "..." }], "confidence": 0.95, "addressed_in_document": true }` | Generate grounded answer strictly from chunks |
| `GET` | `/internal/health` | None (Localhost / Docker Healthcheck Only) | None | 200 OK: `{ "status": "ok", "provider": "gemini", "tesseract_available": true }` | Liveness and health check |

---

## 3. Database Schema

PostgreSQL 16+ schema managed exclusively by Flyway migrations (`V1__init_schema.sql`, `V2__add_indexes.sql`). Hibernate configuration enforces `ddl-auto: validate`. All primary keys are UUIDs generated by `gen_random_uuid()`. **Every table contains both `created_at` and `updated_at` with timezone.**

```sql
-- V1__init_schema.sql

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'USER',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 0,
    is_scanned BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(50) NOT NULL DEFAULT 'UPLOADED',
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE document_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
    title VARCHAR(255),
    document_type VARCHAR(100),
    purpose TEXT,
    parties JSONB NOT NULL DEFAULT '[]'::jsonb,
    summary_short TEXT NOT NULL,
    summary_detailed TEXT NOT NULL,
    main_conditions JSONB NOT NULL DEFAULT '[]'::jsonb,
    obligations_summary JSONB NOT NULL DEFAULT '[]'::jsonb,
    financial_terms_summary JSONB NOT NULL DEFAULT '[]'::jsonb,
    llm_provider VARCHAR(50) NOT NULL,
    llm_model VARCHAR(100) NOT NULL,
    verification_rate NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE extracted_clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES document_analyses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    custom_label VARCHAR(100),
    original_text TEXT NOT NULL,
    simplified_simple TEXT NOT NULL,
    simplified_detailed TEXT NOT NULL,
    simplified_professional TEXT NOT NULL,
    importance VARCHAR(20) NOT NULL,
    affected_party VARCHAR(255),
    source_page INTEGER NOT NULL,
    section_reference VARCHAR(100),
    evidence_quote TEXT NOT NULL,
    quote_verified BOOLEAN NOT NULL DEFAULT FALSE,
    provenance VARCHAR(30) NOT NULL DEFAULT 'EXTRACTED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE risk_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES document_analyses(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    original_clause TEXT NOT NULL,
    explanation TEXT NOT NULL,
    why_it_matters TEXT NOT NULL,
    possible_consequences TEXT NOT NULL,
    suggested_questions JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_page INTEGER NOT NULL,
    evidence_quote TEXT NOT NULL,
    quote_verified BOOLEAN NOT NULL DEFAULT FALSE,
    jurisdiction_caveat TEXT,
    provenance VARCHAR(30) NOT NULL DEFAULT 'AI_INTERPRETATION',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE extracted_information (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL UNIQUE REFERENCES document_analyses(id) ON DELETE CASCADE,
    contract_amount VARCHAR(255) NOT NULL DEFAULT 'Not specified',
    contract_amount_page INTEGER,
    payment_deadlines TEXT NOT NULL DEFAULT 'Not specified',
    payment_deadlines_page INTEGER,
    penalties TEXT NOT NULL DEFAULT 'Not specified',
    penalties_page INTEGER,
    start_date VARCHAR(100) NOT NULL DEFAULT 'Not specified',
    start_date_page INTEGER,
    end_date VARCHAR(100) NOT NULL DEFAULT 'Not specified',
    end_date_page INTEGER,
    renewal_date VARCHAR(100) NOT NULL DEFAULT 'Not specified',
    renewal_date_page INTEGER,
    notice_period VARCHAR(255) NOT NULL DEFAULT 'Not specified',
    notice_period_page INTEGER,
    termination_conditions TEXT NOT NULL DEFAULT 'Not specified',
    termination_conditions_page INTEGER,
    obligations JSONB NOT NULL DEFAULT '[]'::jsonb,
    important_dates JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE missing_clause_warnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES document_analyses(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    clause_name VARCHAR(255) NOT NULL,
    why_it_matters TEXT NOT NULL,
    typical_provision TEXT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    label VARCHAR(50) NOT NULL DEFAULT 'Possible omission',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0,
    search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'General Inquiries',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES chat_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    citations JSONB NOT NULL DEFAULT '[]'::jsonb,
    addressed_in_document BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

```sql
-- V2__add_indexes.sql

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_user_hash ON documents(user_id, file_hash);
CREATE INDEX idx_analyses_document_id ON document_analyses(document_id);
CREATE INDEX idx_clauses_analysis_id ON extracted_clauses(analysis_id);
CREATE INDEX idx_clauses_category ON extracted_clauses(category);
CREATE INDEX idx_clauses_importance ON extracted_clauses(importance);
CREATE INDEX idx_risks_analysis_id ON risk_findings(analysis_id);
CREATE INDEX idx_risks_level ON risk_findings(level);
CREATE INDEX idx_risks_category ON risk_findings(category);
CREATE INDEX idx_missing_clauses_analysis_id ON missing_clause_warnings(analysis_id);
CREATE INDEX idx_chunks_doc_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_search_vector ON document_chunks USING GIN(search_vector);
CREATE INDEX idx_chat_conv_doc_user ON chat_conversations(document_id, user_id);
CREATE INDEX idx_chat_messages_conv_id ON chat_messages(conversation_id);
```

### Full-Text Search Retrieval Query
For document chat retrieval without an external vector database, Spring Boot executes:
```sql
SELECT id, page_number, content,
       ts_rank(search_vector, plainto_tsquery('english', :userQuestion)) AS rank
FROM document_chunks
WHERE document_id = :documentId
  AND search_vector @@ plainto_tsquery('english', :userQuestion)
ORDER BY rank DESC
LIMIT :topK;
```

---

## 4. JSON Schemas for AI Outputs

Every response from the LLM is parsed into validated Pydantic models. On validation error, the engine retries up to 2 times with validation error context appended before surfacing a typed error.

### Quality and Grounding Rules Enforced in Schemas & Prompts:
1. **Provenance Tagging**: Every field carries `EXTRACTED` (verbatim/factual from document) or `AI_INTERPRETATION` (explanation, risks, recommendations).
2. **Missing Fields**: Missing dates, amounts, or parties return exactly `"Not specified"`. Never guess or extrapolate.
3. **No Legal Conclusions**: Prompts strictly prohibit terms like "illegal", "void", or "unenforceable". Findings use objective phrasing like "may be unfavorable" or "you may want to ask about...". Missing clauses are labeled `"Possible omission"`. Risk findings include a `jurisdiction_caveat` when governing law is unknown.
4. **Temperature Settings**: Extraction tasks run at temperature `0.0–0.1`. Plain-language simplifications run at temperature `0.2`.
5. **Prompt-Injection Delimiters**: Raw document content is enclosed inside `<document_content>...</document_content>` tags, accompanied by instructions to treat the block exclusively as unparsed data.

### 4.1 Document Summary (`DocumentSummarySchema`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DocumentSummarySchema",
  "type": "object",
  "properties": {
    "title": { "type": "string" },
    "document_type": { "type": "string" },
    "purpose": { "type": "string" },
    "parties": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "role": { "type": "string" }
        },
        "required": ["name", "role"]
      }
    },
    "summary_short": { "type": "string" },
    "summary_detailed": { "type": "string" },
    "main_conditions": {
      "type": "array",
      "items": { "type": "string" }
    },
    "obligations_summary": {
      "type": "array",
      "items": { "type": "string" }
    },
    "financial_terms_summary": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": [
    "title",
    "document_type",
    "purpose",
    "parties",
    "summary_short",
    "summary_detailed",
    "main_conditions",
    "obligations_summary",
    "financial_terms_summary"
  ]
}
```

### 4.2 Extracted Clause (`ClauseItemSchema` and `ClauseListSchema`)

Includes the 17 named categories plus `Other` (with `custom_label`), and 3 explanation levels: Simple English, Detailed, and Professional.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ClauseListSchema",
  "type": "object",
  "properties": {
    "clauses": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": { "type": "string" },
          "category": {
            "type": "string",
            "enum": [
              "Confidentiality",
              "Termination",
              "Intellectual Property",
              "Liability and Indemnification",
              "Dispute Resolution",
              "Governing Law",
              "Payment Terms",
              "Representations and Warranties",
              "Non-Compete and Non-Solicitation",
              "Force Majeure",
              "Assignment",
              "Severability",
              "Amendment",
              "Notices",
              "Term and Renewal",
              "Data Protection and Privacy",
              "Insurance",
              "Other"
            ]
          },
          "custom_label": { "type": ["string", "null"] },
          "original_text": { "type": "string" },
          "simplified_simple": { "type": "string" },
          "simplified_detailed": { "type": "string" },
          "simplified_professional": { "type": "string" },
          "importance": {
            "type": "string",
            "enum": ["HIGH", "MEDIUM", "LOW"]
          },
          "affected_party": { "type": "string" },
          "source_page": { "type": "integer", "minimum": 1 },
          "section_reference": { "type": ["string", "null"] },
          "evidence_quote": { "type": "string" },
          "quote_verified": { "type": "boolean", "default": false },
          "provenance": {
            "type": "string",
            "enum": ["EXTRACTED", "AI_INTERPRETATION"],
            "default": "EXTRACTED"
          }
        },
        "required": [
          "title",
          "category",
          "original_text",
          "simplified_simple",
          "simplified_detailed",
          "simplified_professional",
          "importance",
          "affected_party",
          "source_page",
          "evidence_quote"
        ]
      }
    }
  },
  "required": ["clauses"]
}
```

### 4.3 Risk Finding (`RiskItemSchema` and `RiskListSchema`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RiskListSchema",
  "type": "object",
  "properties": {
    "risks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string",
            "enum": [
              "FINANCIAL",
              "LEGAL",
              "PRIVACY",
              "CONTRACTUAL",
              "EMPLOYMENT",
              "LIABILITY"
            ]
          },
          "level": {
            "type": "string",
            "enum": ["HIGH", "MEDIUM", "LOW", "INFORMATIONAL"]
          },
          "title": { "type": "string" },
          "original_clause": { "type": "string" },
          "explanation": { "type": "string" },
          "why_it_matters": { "type": "string" },
          "possible_consequences": { "type": "string" },
          "suggested_questions": {
            "type": "array",
            "items": { "type": "string" }
          },
          "source_page": { "type": "integer", "minimum": 1 },
          "evidence_quote": { "type": "string" },
          "quote_verified": { "type": "boolean", "default": false },
          "jurisdiction_caveat": { "type": ["string", "null"] },
          "provenance": {
            "type": "string",
            "enum": ["EXTRACTED", "AI_INTERPRETATION"],
            "default": "AI_INTERPRETATION"
          }
        },
        "required": [
          "category",
          "level",
          "title",
          "original_clause",
          "explanation",
          "why_it_matters",
          "possible_consequences",
          "suggested_questions",
          "source_page",
          "evidence_quote"
        ]
      }
    }
  },
  "required": ["risks"]
}
```

### 4.4 Key Information (`KeyInformationSchema`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "KeyInformationSchema",
  "type": "object",
  "properties": {
    "contract_amount": { "type": "string" },
    "contract_amount_page": { "type": ["integer", "null"] },
    "payment_deadlines": { "type": "string" },
    "payment_deadlines_page": { "type": ["integer", "null"] },
    "penalties": { "type": "string" },
    "penalties_page": { "type": ["integer", "null"] },
    "start_date": { "type": "string" },
    "start_date_page": { "type": ["integer", "null"] },
    "end_date": { "type": "string" },
    "end_date_page": { "type": ["integer", "null"] },
    "renewal_date": { "type": "string" },
    "renewal_date_page": { "type": ["integer", "null"] },
    "notice_period": { "type": "string" },
    "notice_period_page": { "type": ["integer", "null"] },
    "termination_conditions": { "type": "string" },
    "termination_conditions_page": { "type": ["integer", "null"] },
    "obligations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "party": { "type": "string" },
          "obligation": { "type": "string" },
          "source_page": { "type": "integer" }
        },
        "required": ["party", "obligation", "source_page"]
      }
    },
    "important_dates": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "label": { "type": "string" },
          "date_value": { "type": "string" },
          "source_page": { "type": "integer" }
        },
        "required": ["label", "date_value", "source_page"]
      }
    }
  },
  "required": [
    "contract_amount",
    "payment_deadlines",
    "penalties",
    "start_date",
    "end_date",
    "renewal_date",
    "notice_period",
    "termination_conditions",
    "obligations",
    "important_dates"
  ]
}
```

### 4.5 Missing Clause (`MissingClauseListSchema`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MissingClauseListSchema",
  "type": "object",
  "properties": {
    "missing_clauses": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "category": { "type": "string" },
          "clause_name": { "type": "string" },
          "why_it_matters": { "type": "string" },
          "typical_provision": { "type": "string" },
          "risk_level": {
            "type": "string",
            "enum": ["HIGH", "MEDIUM", "LOW"]
          },
          "label": {
            "type": "string",
            "default": "Possible omission"
          }
        },
        "required": [
          "category",
          "clause_name",
          "why_it_matters",
          "typical_provision",
          "risk_level",
          "label"
        ]
      }
    }
  },
  "required": ["missing_clauses"]
}
```

### 4.6 Chat Answer (`ChatAnswerSchema`)

If the answer is not present in the retrieved chunks, the model is instructed to output `"The document does not appear to address this."` with `addressed_in_document: false`.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChatAnswerSchema",
  "type": "object",
  "properties": {
    "answer": { "type": "string" },
    "source_chunks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "chunk_id": { "type": "string" },
          "page_number": { "type": "integer" },
          "quote": { "type": "string" }
        },
        "required": ["chunk_id", "page_number", "quote"]
      }
    },
    "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "addressed_in_document": { "type": "boolean" }
  },
  "required": ["answer", "source_chunks", "confidence", "addressed_in_document"]
}
```

---

## 5. Async Job State Machine & Deduplication Flow

The document analysis pipeline is asynchronous to prevent browser request timeouts.

```
+--------------------------------------------------------------------+
|                         Client uploads file                        |
+--------------------------------------------------------------------+
                                  |
                                  v
+--------------------------------------------------------------------+
|  1. Spring Boot: POST /api/documents/upload                        |
|     - Validate file size (<10MB) & magic bytes (PDF, DOCX, TXT)    |
|     - Compute SHA-256 hash                                         |
|     - Query documents WHERE user_id = :uid AND file_hash = :hash   |
|     - If existing document found AND forceReanalyze is false:      |
|         Return HTTP 409 Conflict with duplicate analysis details   |
|         (Client displays modal: reuse analysis or force re-run)    |
|     - If new or forceReanalyze is true:                            |
|         Save file with UUID filename in local storage directory    |
|         Insert Document record with status = 'UPLOADED'            |
|         Return HTTP 202 Accepted with document id                  |
+--------------------------------------------------------------------+
                                  |
                Triggers @Async background execution
                                  |
                                  v
+--------------------------------------------------------------------+
|  2. Status -> 'EXTRACTING'                                         |
|     - Call FastAPI POST /internal/extract                          |
|     - Parse PDF / DOCX / TXT with PyMuPDF or python-docx           |
|     - Check character density; if scanned PDF, invoke Tesseract    |
|     - Fast API returns page texts & chunk list                     |
|     - Spring Boot writes chunks to document_chunks table           |
|       (PostgreSQL automatically computes tsvector)                 |
+--------------------------------------------------------------------+
                                  |
                                  v
+--------------------------------------------------------------------+
|  3. Status -> 'ANALYZING'                                          |
|     - Spring Boot calls FastAPI POST /internal/analyze             |
|     - Map-reduce analysis over chunks:                             |
|         a. Extract candidate clauses, risks, key terms             |
|         b. Merge and deduplicate across chunks                     |
|         c. Generate concise and detailed summaries                 |
|         d. Detect missing standard clauses by document type        |
|     - Evidence verification: check quotes against page text        |
|       (normalize whitespace, case-insensitive, fuzzy >= 0.9)      |
|     - Compute analysis verification rate:                          |
|         rate = (verified_quotes_count / total_quotes_count) * 100   |
|     - Persist analysis, clauses, risks, key_info, missing_clauses  |
+--------------------------------------------------------------------+
                |                                    |
          On Success                              On Error
                |                                    |
                v                                    v
+-----------------------------+       +------------------------------+
|  4. Status -> 'COMPLETED'   |       |  5. Status -> 'FAILED'       |
|     - Ready for viewer,     |       |     - failure_reason set     |
|       dashboard, chat,      |       |     - Frontend shows error   |
|       and PDF report        |       |       with actionable advice |
+-----------------------------+       +------------------------------+
```

### State Transitions and Polling Protocol
- Frontend initiates `POST /api/documents/upload` and receives `{ "id": "...", "status": "UPLOADED" }`.
- Frontend polls `GET /api/documents/{id}/status` every 2.5 seconds.
- Valid status values: `UPLOADED`, `EXTRACTING`, `ANALYZING`, `COMPLETED`, `FAILED`.
- Polling stops immediately upon reaching `COMPLETED` or `FAILED`.
- If `status == FAILED`, the response includes `failure_reason` (e.g., "The document is password-protected or unreadable").

---

## 6. PDF Report Specification (10 Sections)

Generated on the fly by OpenPDF in Spring Boot via `GET /api/documents/{id}/report`. Every finding cites the original page and carries the `[EXTRACTED]` or `[AI_INTERPRETATION]` provenance label.

The 10 mandatory sections are:
1. **Overview**: Document title, detected type, analysis date, party names and roles, page count, and quote verification rate.
2. **Executive Summary**: Short summary and comprehensive detailed summary.
3. **Important Clauses**: Categorized clauses, importance badges (High/Medium/Low), original text, and source page citations.
4. **Plain-Language Explanations**: Side-by-side or stacked simplified versions (Simple English, Detailed, Professional) for each extracted clause.
5. **Risk Analysis**: Identified risks categorized into Financial, Legal, Privacy, Contractual, Employment, or Liability, with severity level, explanation, and consequences.
6. **Financial Terms**: Summary of contract amounts, payment schedules, and financial liabilities.
7. **Important Dates & Deadlines**: Start date, expiration date, renewal notice periods, and commercial milestones.
8. **Missing Provisions**: Potential omissions based on contract type, labeled "Possible omission", explaining standard industry provisions.
9. **Suggested Questions to Ask**: Actionable negotiation questions derived from identified risks and ambiguous terms.
10. **Legal Disclaimer & Jurisdiction Caveats**: Explicit notice that the report is an automated informational aid and does not constitute formal legal counsel.

---

## 7. Frontend Architecture & LegalTech Design Tokens

- **Palette**: Deep Navy (`#0F172A`) as the primary tone, clean slate neutrals (`#F8FAFC` background, `#E2E8F0` borders), subtle accent blue (`#2563EB`), and muted semantic tones for risk (Red `#DC2626`, Amber `#D97706`, Green `#16A34A`, Blue `#2563EB`).
- **Typography**: Editorial serif font (Source Serif 4) for headings; crisp sans-serif (Inter) for UI controls, tables, and document text.
- **Components & Layouts**:
  - `ThemeContext.jsx` supporting light and dark mode toggles with persistence in `localStorage`.
  - Side-by-side Document Viewer: Clicking any clause, risk, or key item highlights the cited `source_page` and navigates the viewer to the exact text quote.
  - Upload Privacy Modal: One-time consent dialog explaining that document text is transmitted to Gemini API when `LLM_PROVIDER=gemini`.
  - Duplicate File Modal: Alerts user when a document hash matches a previous upload, offering one-click navigation to the existing analysis.

---

## 8. Risk List and Technical Mitigations

| Risk | Likelihood | Impact | Technical Mitigation |
|---|---|---|---|
| **Hallucinated clauses or false citations** | Medium | High | Two-stage grounding pipeline: strict Pydantic output schema requiring verbatim `evidence_quote` and `source_page`; automated post-LLM quote verifier searching page text using normalized fuzzy matching (ratio >= 0.9). Unverified items are flagged with `quote_verified = false` and displayed with alert badges. |
| **Context length overflow on multi-page contracts** | High | High | Text chunker with page awareness (~3,500 tokens with 250 token overlap). Map-reduce workflow: chunk-level clause extraction followed by a merge/deduplication pass and final summary pass. |
| **Prompt injection embedded in uploaded contracts** | Medium | High | Contract text is treated strictly as passive data, wrapped in unambiguous delimiters (`<document_content>...</document_content>`). System prompts explicitly instruct the model never to execute instructions found in document text. Injection test case (`prompt_injection_test.txt`) included in test suite. |
| **Low-quality scanned documents failing text extraction** | Medium | Medium | PyMuPDF text heuristic checks if character count per page is below threshold. Scanned pages are automatically routed to Tesseract OCR with grayscale and contrast preprocessing. `is_scanned` flag is stored and shown in metadata. |
| **Gemini API rate limiting (429 HTTP status)** | Medium | High | Exponential backoff with jitter on API calls. Configurable `LLM_PROVIDER` environment variable allows immediate local fallback to Ollama without changing application code. |
| **Malicious or oversized file uploads** | Low | High | Spring Boot validates file size (maximum 10 MB limit) and validates file magic bytes (rejecting disguised executables). Files are stored outside any web root with random UUID filenames. |
| **Unauthorized access across users** | Low | High | All database queries enforce `user_id = principal.id`. Endpoints querying by document ID return HTTP 404 (not 403) when accessed by non-owners to prevent identifier enumeration. |
| **Heavy full-text search load in PostgreSQL** | Low | Medium | tsvector column is stored and indexed with GIN (`idx_chunks_search_vector`). Chat queries retrieve top-k chunks with page limit before sending to LLM. |
| **PDF report rendering memory spikes** | Low | Medium | OpenPDF streams report generation directly to response output stream without building uncompressed raster images in memory. |
| **Brute-force credential attempts on auth routes** | Medium | Medium | In-memory token bucket rate limiter (`RateLimitingFilter.java`) restricting `/api/auth/login` and `/api/auth/register` to 5 requests per minute per IP. |
