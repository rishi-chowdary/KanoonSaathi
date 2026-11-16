# LexiLegal AI — Project Progress

This document tracks implementation status across the 10 phases of the project. Each phase records what was built, how it was verified, known issues, and the exact commands to run.

---

## Overall Status Summary

| Phase | Description | Status | Completed Date |
|---|---|---|---|
| Phase 1 | Toolchain Setup & Project Scaffolding | Completed | 2026-11-16 |
| Phase 2 | Database Schema, All Entities & Complete Auth Flow (Backend + Frontend) | Completed | 2026-11-16 |
| Phase 3 | Document Extraction, OCR, Chunking, Upload Pipeline & Text Preview (Full Stack) | Completed | 2026-11-17 |
| Phase 4 | FastAPI AI Engine: LLM Providers, Structured Analysis & Quote Verification | Not Started | - |
| Phase 5 | Spring Boot Backend: Document Storage, Hash Caching & Async Pipeline | Not Started | - |
| Phase 6 | Spring Boot Backend: Analysis Persistence & Full-Text Search Retrieval | Not Started | - |
| Phase 7 | Spring Boot Backend: OpenPDF Report Generation & Dashboard Statistics | Not Started | - |
| Phase 8 | Frontend: Document Upload, Progress Polling & File Validation | Not Started | - |
| Phase 9 | Frontend: Analysis Workspace, Side-by-Side Viewer & Grounded Chat | Not Started | - |
| Phase 10 | Evaluation Suite, End-to-End Testing & Viva Preparation | Not Started | - |

---

## Phase Checklist

### Phase 1: Toolchain Setup & Project Scaffolding
- [x] Inspect host toolchain (Java, Maven, Node, npm, Python, PostgreSQL, Docker, Git, Tesseract)
- [x] Produce architecture and implementation plan (`docs/implementation-plan.md`)
- [x] Initialize progress tracking (`docs/PROGRESS.md`)
- [x] Initialize git repository on `main` branch
- [x] Verify Tesseract OCR availability flag in AI engine
- [x] Scaffold directory structure for `frontend`, `backend`, `ai-engine`, `samples`, `evaluation`, and `postman`
- [x] Set up `.env.example`, `.env`, `.gitignore`, and base Docker Compose configuration
- [x] Verify PostgreSQL connectivity and database initialization via Flyway migrations (`V1__init_schema.sql`, `V2__add_indexes.sql`)
- [x] Implement FastAPI AI engine with `/health`, `/internal/health`, `X-Internal-Api-Key` header authentication, and unit tests
- [x] Implement Spring Boot 3 backend (Java 21) with Web, Security, JPA, Flyway, Swagger UI, CORS, `GET /api/health`, and `GET /api/health/ai`
- [x] Implement React 18 + Vite frontend shell with Tailwind CSS, Lucide icons, dark/light theme persistence, AppLayout, AuthLayout, and route placeholders
- [x] Verify full stack execution: frontend, backend, database, and AI engine running with verified service-to-service authentication

**What was built:**
- Directory tree scaffolded for all 3 tiers and shared assets (`frontend`, `backend`, `ai-engine`, `database`, `samples`, `evaluation`, `postman`, `docs`).
- Root configuration: `.gitignore`, `.env.example`, `.env`, `docker-compose.yml`, and `README.md`.
- FastAPI AI Engine (`ai-engine/`):
  - Configuration via `pydantic-settings` reading `.env`.
  - Structured request logging middleware.
  - `GET /health` public endpoint.
  - `GET /internal/health` protected by `X-Internal-Api-Key` header check.
  - 4 automated pytest unit tests covering health and auth behavior.
- Spring Boot 3 Backend (`backend/`):
  - Maven project configured with Java 21 compilation target.
  - Security configuration with stateless session management, CSRF disabled, and CORS configured for `http://localhost:5173`.
  - Flyway migrations `V1__init_schema.sql` (10 tables with `created_at` and `updated_at`) and `V2__add_indexes.sql` applied to PostgreSQL.
  - `AiEngineClient` using Spring 6 `RestClient` to call FastAPI with `X-Internal-Api-Key`.
  - `HealthController` with `GET /api/health` (DB connectivity check) and `GET /api/health/ai` (service-to-service auth verification).
  - Swagger UI configured at `/swagger-ui.html` and OpenAPI docs at `/v3/api-docs`.
- React 18 Frontend (`frontend/`):
  - Vite + React + Tailwind CSS with legal-tech palette (Navy/White, editorial font).
  - `ThemeContext` persisting dark/light mode choice in `localStorage`.
  - `AppLayout` with responsive `Navbar` and `Footer`.
  - `AuthLayout` for sign-in/registration flows.
  - Route placeholders for Landing, Login, Register, Dashboard, Upload, Analysis, History, and Profile pages.
  - Pre-configured Axios instance with auth interceptor.

**How it was verified:**
- PostgreSQL Container: `docker compose up -d postgres` running `postgres:16-alpine`, port `5433:5432`, volume `lexilegal_pgdata`. Healthcheck status confirmed `healthy`.
- FastAPI: `cd ai-engine && .venv/bin/pytest` -> 4 passed. Running on port 8000.
  - `curl -i http://127.0.0.1:8000/health` -> HTTP 200 OK.
  - `curl -i http://127.0.0.1:8000/internal/health` (without key) -> HTTP 401 Unauthorized.
  - `curl -i -H "X-Internal-Api-Key: wrong" http://127.0.0.1:8000/internal/health` -> HTTP 401 Unauthorized.
  - `curl -i -H "X-Internal-Api-Key: <key>" http://127.0.0.1:8000/internal/health` -> HTTP 200 OK.
- Spring Boot: `mvn test-compile` and `mvn spring-boot:run`. Flyway applied schema version 1 and 2 to PostgreSQL.
  - `GET /api/health` -> HTTP 200 `{"status":"ok","database":"connected","service":"lexilegal-backend"}`.
  - `GET /api/health/ai` -> HTTP 200 `{"status":"ok","service_to_service_auth":"verified","ai_engine":{"status":"ok","service":"ai-engine","provider":"gemini","tesseract_available":false}}`.
  - Swagger UI: `/swagger-ui.html` redirects to `/swagger-ui/index.html` (HTTP 200). OpenAPI spec available at `/v3/api-docs` (HTTP 200).
  - CORS: OPTIONS preflight from `http://localhost:5173` returned HTTP 200 with `Access-Control-Allow-Origin: http://localhost:5173`.
- Frontend: `npm run build` bundled production assets cleanly. Preview server running on port 5173.
  - Automated browser test via headless Chrome (`node frontend/test-e2e.cjs`):
    - Verified landing page heading and title.
    - Verified theme toggle switch: adds `dark` class, updates `localStorage.getItem("lexilegal_theme") = "dark"`.
    - Verified persistence: page reload maintains `dark` class and `localStorage`.
    - Verified all placeholder routes render successfully: `/dashboard`, `/upload`, `/documents/:id`, `/history`, `/profile`, `/login`, `/register`.
- Secrets & Gitignore: `.env` and `.env.local` confirmed gitignored (`git check-ignore`). No private keys or real API keys tracked.

**Exact commands to run and test:**
```bash
# 1. AI Engine
cd ai-engine
.venv/bin/pytest
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

# 2. Backend
cd backend
mvn spring-boot:run

# 3. Test health and auth
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/health/ai

# 4. Frontend
cd frontend
npm run build
npm run preview -- --port 5173 --host 127.0.0.1
```

---

### Phase 2: Database Schema, All Entities & Complete Auth Flow (Backend + Frontend)
- [x] Create Flyway migration `V1__init_schema.sql` creating all 10 tables: `users`, `documents`, `document_analyses`, `extracted_clauses`, `risk_findings`, `extracted_information`, `missing_clause_warnings`, `chat_conversations`, `chat_messages`, `document_chunks`
- [x] Configure UUID primary keys, foreign key constraints with `ON DELETE CASCADE`, and timestamps (`created_at`, `updated_at`) across all tables
- [x] Create Flyway migration `V2__add_indexes.sql` creating B-Tree indexes on foreign keys, hashes, and a GIN tsvector full-text search index on `document_chunks.search_vector`
- [x] Implement `BaseEntity` with `@CreationTimestamp` and `@UpdateTimestamp` auditing
- [x] Implement JPA entities for all 10 schema tables with proper relations and Jackson JSON serialization mappings
- [x] Implement Spring Data JPA repositories for all 10 entities
- [x] Configure stateless Spring Security with BCrypt password hashing (`PasswordEncoder`)
- [x] Implement JWT token generator and validator (`JwtTokenProvider`) using `io.jsonwebtoken` (HMAC-SHA256)
- [x] Implement once-per-request JWT authentication filter (`JwtAuthFilter`) and custom `UserPrincipal`
- [x] Implement authentication service with in-memory IP rate limiting (`LoginRateLimiter`: max 5 failed attempts per minute)
- [x] Implement auth endpoints:
  - `POST /api/auth/register` (email format and uniqueness check, password min 8 chars with letter + digit)
  - `POST /api/auth/login` (stateless JWT issue, returns user details and token)
  - `GET /api/users/me` (returns authenticated user profile)
  - `PUT /api/users/me` (updates full name and optional password change)
  - `POST /api/auth/logout` (acknowledged client-side token discard)
- [x] Implement `GlobalExceptionHandler` returning structured `ErrorResponse` (400 validation, 401 bad credentials, 404 resource not found/access denied, 409 conflict, 429 rate limit)
- [x] Implement frontend authentication system:
  - `AuthContext` and `useAuth` hook managing token, user session, and auth actions
  - Axios interceptor attaching `Authorization: Bearer <token>` on all requests and auto-redirecting to `/login` on 401
  - `ProtectedRoute` component guarding `/dashboard`, `/upload`, `/history`, and `/profile`
  - Responsive `Navbar` displaying user full name, profile settings link, and Sign Out action
  - Functional `RegisterPage`, `LoginPage`, and `ProfilePage` with form validation, error banners, and loading states
- [x] Write backend integration test suite (`AuthControllerTest.java`): 8 tests verifying registration success, duplicate email conflict, password complexity validation, login success, wrong password rejection, protected route without token (401), and protected route with token (200)
- [x] Write automated frontend E2E browser test suites (`test-e2e.cjs` and `test-auth-e2e.cjs`) verifying protected route redirects, registration, navbar user display, profile update, logout, and login

**What was built:**
- Backend:
  - Flyway migrations: `backend/src/main/resources/db/migration/V1__init_schema.sql` and `V2__add_indexes.sql`
  - JPA Entities: `BaseEntity`, `User`, `Document`, `DocumentAnalysis`, `ExtractedClause`, `RiskFinding`, `ExtractedInformation`, `MissingClauseWarning`, `DocumentChunk`, `ChatConversation`, `ChatMessage`
  - Repositories: 10 Spring Data JPA repository interfaces in `com.lexilegal.repository`
  - Security & Auth: `JwtTokenProvider`, `JwtAuthFilter`, `UserPrincipal`, `CustomUserDetailsService`, `LoginRateLimiter`, `SecurityConfig`, `CorsConfig`
  - Controllers & Services: `AuthController`, `UserController`, `AuthService`, `UserService`
  - Exception Handling: `GlobalExceptionHandler`, `DuplicateEmailException`, `ResourceNotFoundException`, `RateLimitExceededException`, `ErrorResponse`
  - Automated Integration Tests: `AuthControllerTest` with 8 test cases
- Frontend:
  - `src/context/AuthContext.jsx` & `src/hooks/useAuth.js`
  - `src/services/api.js` with Bearer request interceptor and 401 response interceptor
  - `src/components/common/ProtectedRoute.jsx`
  - `src/components/common/Navbar.jsx` with active route styling and user dropdown menu
  - `src/pages/RegisterPage.jsx`, `src/pages/LoginPage.jsx`, `src/pages/ProfilePage.jsx`
  - `test-auth-e2e.cjs` automated Puppeteer test suite
  - `verify-browser-flow.cjs` targeted browser flow verification script
- Postman:
  - `postman/lexilegal.postman_collection.json` covering registration, duplicate handling, password complexity, login, wrong password rejection, user retrieval with/without token, profile update, logout, and service health checks.

**How it was verified:**
- Backend Integration Tests (`mvn test`):
  - 8 tests executed, 0 failures, 0 errors, 0 skipped (`BUILD SUCCESS`).
- Postman Collection & Direct API Verification:
  - `POST /api/auth/register` with valid payload -> HTTP 201 Created (JWT issued, user profile returned)
  - `POST /api/auth/register` duplicate email -> HTTP 409 Conflict (`an account with this email already exists`)
  - `POST /api/auth/register` weak password ("weak") -> HTTP 400 Bad Request (`fieldErrors.password`: must be at least 8 chars with letter + digit)
  - `POST /api/auth/login` with wrong password -> HTTP 401 Unauthorized (`invalid email or password`)
  - `POST /api/auth/login` with correct credentials -> HTTP 200 OK (JWT issued)
  - `GET /api/users/me` without token -> HTTP 401 Unauthorized (`unauthorized: authentication required`)
  - `GET /api/users/me` with valid token -> HTTP 200 OK (returns user profile)
  - `PUT /api/users/me` with valid token -> HTTP 200 OK (updates profile)
  - Rate Limiter: 5 failed login attempts return 401; 6th attempt returns HTTP 429 Too Many Requests
  - CORS Preflight: `OPTIONS /api/auth/register` from `http://127.0.0.1:5173` returns HTTP 200 with `Access-Control-Allow-Origin: http://127.0.0.1:5173`
- Database Inspection with `psql`:
  - Relations list (`\dt`) confirms all 11 tables exist: `chat_conversations`, `chat_messages`, `document_analyses`, `document_chunks`, `documents`, `extracted_clauses`, `extracted_information`, `flyway_schema_history`, `missing_clause_warnings`, `risk_findings`, `users`.
  - Passwords in `users.password_hash` confirmed to be standard 60-character BCrypt hashes (`$2a$10$...`), never plaintext.
  - `flyway_schema_history` confirmed: rank 1 (`V1__init_schema.sql`) and rank 2 (`V2__add_indexes.sql`) both executed with `success = t`.
  - Hibernate schema validation (`hibernate.ddl-auto: validate`) boots cleanly with zero entity-schema discrepancies.
- Browser Flow Verification (`node frontend/verify-browser-flow.cjs`):
  - Register new account on `/register` -> auto-redirects to `/dashboard`
  - Sign out via user menu -> redirects to `/login`
  - Log in with newly created credentials -> redirects to `/dashboard`
  - Navigate to `/profile` -> update full name -> updates profile and Navbar display
  - Log out -> redirects to `/login`
  - Attempt to visit `/dashboard` directly while logged out -> immediately redirects to `/login`
- Expired & Tampered Token Verification:
  - Tampered signature token -> HTTP 401 Unauthorized (`unauthorized: authentication required`)
  - Tampered payload token -> HTTP 401 Unauthorized (`unauthorized: authentication required`)
  - Expired token (`exp` timestamp in the past) -> HTTP 401 Unauthorized (`unauthorized: authentication required`)
  - Malformed token string -> HTTP 401 Unauthorized (`unauthorized: authentication required`)

**Exact commands to run and test:**
```bash
# 1. Run Backend Unit & Integration Tests
cd backend
mvn test

# 2. Run Backend Application Server
mvn spring-boot:run

# 3. Build and Preview Frontend
cd frontend
npm run build
npm run preview -- --port 5173 --host 127.0.0.1

# 4. Run Frontend E2E Tests
node frontend/test-e2e.cjs
node frontend/test-auth-e2e.cjs
```

---

### Phase 3: Document Extraction, OCR, Chunking, Upload Pipeline & Text Preview (Full Stack)
- [x] Implement AI Engine text extractors for PDF (PyMuPDF) with page numbers and text blocks
- [x] Implement scanned page detection (< 50 chars) and Tesseract OCR fallback (page -> PNG image -> pytesseract)
- [x] Implement DOCX extractor (python-docx) extracting paragraphs, tables, and section headings with page-break heuristics
- [x] Implement TXT extractor with virtual page splitting (~3000 chars per page)
- [x] Implement section heading detector regex (`1.`, `1.1`, `Article IV`, `Clause 7`) attaching `section_ref`
- [x] Define typed extraction error codes (`CORRUPTED_FILE`, `PASSWORD_PROTECTED`, `EMPTY_FILE`, `UNSUPPORTED_TYPE`)
- [x] Implement page-aware and section-aware text chunker (~3–4k tokens, 200 token overlap) preserving `page_start`, `page_end`, and `section_ref`
- [x] Expose protected `POST /internal/extract` and public `POST /extract` endpoints in FastAPI
- [x] Build Spring Boot `DocumentStorageService`: magic byte validation (`%PDF-`, `PK\x03\x04`, text binary check, rejecting `MZ` / `.exe`), 10MB limit, SHA-256 computation, randomized storage outside web root (`uploads/`), and file deletion
- [x] Implement per-user SHA-256 duplicate detection returning existing document with `duplicate: true`
- [x] Implement `@Async` pipeline in Spring Boot: `UPLOADED` -> `EXTRACTING` (calls AI engine `/internal/extract`) -> saves chunks with tsvector -> `EXTRACTED` (or `FAILED` with failure reason)
- [x] Implement `DocumentController` endpoints: `POST /api/documents/upload` (202 Accepted), `GET /api/documents` (paginated, search, status filter), `GET /api/documents/{id}`, `GET /api/documents/{id}/status`, `GET /api/documents/{id}/text?page=N`, and `DELETE /api/documents/{id}`
- [x] Enforce strict user ownership across all document endpoints (returning HTTP 404 for documents owned by other users to prevent ID enumeration)
- [x] Build frontend `UploadPage`: drag-and-drop, file picker, file size/type client validation, privacy consent checkbox, upload progress bar, status polling stepper (`Uploaded` -> `Extracting` -> `Extracted`), and duplicate notification
- [x] Build frontend `HistoryPage`: document search, status filter, paginated vault table, status badges, and delete action with confirmation modal
- [x] Build frontend `AnalysisPage` document viewer: page text preview with page navigation controls (Prev/Next) and metadata banner
- [x] Generate 7 sample contracts in `samples/contracts/`: clean text PDF, DOCX, TXT, scanned PDF, corrupted PDF, empty file, and renamed `.exe` to `.pdf`
- [x] Add automated Postman collection requests for Document Upload, Status, Pagination, Text by Page, and Delete
- [x] Verify end-to-end with automated browser test (`test-phase3-e2e.cjs`), pytest suite (11 tests), backend integration tests (15 tests), and automated pipeline script

**What was built:**
- AI Engine (`ai-engine/`):
  - `app/schemas/extraction.py`: Pydantic models for `PageExtraction`, `SectionExtraction`, `ChunkExtraction`, `ExtractionResponse`, and `ExtractionErrorResponse`.
  - `app/services/extractor.py`: Multi-format document parser handling PDF via PyMuPDF, scanned PDF via Tesseract OCR, DOCX via `python-docx` with table flattening, and TXT with virtual pagination. Regex heading detector tagging clauses (`Article [IVXLCDM]+`, `Section \d+`, `\d+\.\d+`, etc.).
  - `app/services/chunker.py`: Page-aware chunking preserving exact `page_start`, `page_end`, and `section_ref` for citations.
  - `app/api/routes.py`: Mounted `POST /internal/extract` (internal key) and `POST /extract` (public/doc-facing).
  - `tests/test_extraction.py`: 7 automated tests covering all formats, error codes, and authentication.
- Backend (`backend/`):
  - `DocumentStorageService`: File validation (magic bytes, 10MB limit, Windows PE executable rejection), SHA-256 hash calculation, unique disk persistence, and deletion.
  - `AiEngineClient`: Configured with `SimpleClientHttpRequestFactory` (HTTP/1.1 without `h2c` upgrade) and `ByteArrayResource` with filename for multipart transmission to FastAPI.
  - `DocumentAsyncPipeline`: Spring `@Async` service updating document status, delegating extraction to AI Engine, saving chunk records with PostgreSQL tsvector search vectors, and updating page counts.
  - `DocumentController` & `DocumentService`: Complete document lifecycle management with ownership checks (404 on isolation violation), pagination, text preview by page number, and cascade deletion.
  - `DocumentControllerTest`: 7 automated integration tests verifying upload, duplicate hash detection, MZ binary rejection, magic byte mismatch, ownership isolation (User B cannot access User A documents), and deletion.
- Frontend (`frontend/`):
  - `UploadPage.jsx`: Drag-and-drop zone, file size/format validation, required privacy consent notice, progress bar, real-time polling stepper (`Uploaded` -> `Extracting` -> `Extracted`), duplicate notice banner, and link to document viewer.
  - `HistoryPage.jsx`: Document vault table with search input, status dropdown filter, timestamp formatting, status badges, and delete action.
  - `AnalysisPage.jsx`: Document viewer displaying extracted text page by page with navigation controls, page indicators, and loading spinners.
  - `test-phase3-e2e.cjs`: Puppeteer test verifying the full browser flow end to end.
- Sample Contracts (`samples/contracts/`):
  - `clean_nda.pdf`: 2-page text PDF with standard confidentiality sections.
  - `service_agreement.docx`: Word document with headings and tabular terms.
  - `promissory_note.txt`: Plaintext contract with virtual paging.
  - `scanned_deed.pdf`: Image-only PDF requiring Tesseract OCR.
  - `corrupted_contract.pdf`: Damaged PDF header triggering `CORRUPTED_FILE`.
  - `empty_contract.pdf`: 0-byte file triggering `EMPTY_FILE`.
  - `malicious_renamed.exe.pdf`: Renamed PE binary triggering `INVALID_FILE_MAGIC`.

**How it was verified:**
- Backend Integration Tests (`mvn test`):
  - 15 tests executed across `AuthControllerTest`, `DocumentControllerTest`, and `LexiLegalApplicationTests`: 0 failures, 0 errors, 0 skipped (`BUILD SUCCESS`).
- AI Engine Pytest (`pytest`):
  - 11 tests executed across extraction and health test suites: 11 passed in 0.82s.
- End-to-End Browser Flow (`node frontend/test-phase3-e2e.cjs`):
  - User registration -> redirects to `/dashboard`
  - Navigate to `/upload` -> attach `clean_nda.pdf` -> consent checkbox -> click "Upload & Process"
  - Stepper advances from "Uploaded" to "Extracting" to "Extracted" within ~3 seconds
  - Click "View Extracted Text" -> navigates to `/documents/{id}`
  - Verified Page 1 rendered ("NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT", "1. Confidential Information")
  - Click "Next" -> verified Page 2 rendered ("4. Term and Termination", "Delaware")
  - Navigate to `/history` -> document listed in table with "Extracted" badge and 2 pages
  - Click "Delete" -> confirm dialog -> document permanently removed from table
- Negative & Edge Case Verification:
  - Executable (`.exe` renamed to `.pdf`) upload rejected with HTTP 400 Bad Request (`Invalid file format: executable files are prohibited`).
  - Corrupted PDF rejected by AI Engine with typed code `CORRUPTED_FILE`.
  - Empty file upload rejected with HTTP 400 Bad Request (`File is empty`).
  - Duplicate upload returns existing document with `duplicate: true`.
  - Cross-tenant access attempt (User B requesting User A's document) returns HTTP 404 Not Found.

**Exact commands to run and test:**
```bash
# 1. Run AI Engine Unit Tests
cd ai-engine
.venv/bin/pytest

# 2. Run Backend Unit & Integration Tests
cd backend
mvn test

# 3. Build Frontend
cd frontend
npm run build

# 4. Run Frontend E2E Browser Verification
node frontend/test-phase3-e2e.cjs
```

### Phase 4: FastAPI AI Engine — LLM Providers, Structured Analysis & Verification
- [ ] Implement `LLMProvider` abstraction with `GeminiProvider` and `OllamaProvider`
- [ ] Implement exponential backoff for rate limits and connection retries
- [ ] Define Pydantic v2 validation schemas for summary, clauses, risks, key information, and missing clauses
- [ ] Implement map-reduce analysis pipeline for long documents
- [ ] Implement evidence quote verifier with normalized fuzzy matching (threshold >= 0.9)
- [ ] Add prompt injection mitigation tests and delimiters
- [ ] Create `/internal/analyze` and `/internal/chat` endpoints
- [ ] Write unit tests for schemas, verification, and mock LLM flows

### Phase 5: Spring Boot Backend — Document Storage, Hash Caching & Async Pipeline
- [ ] Implement Document entity and DocumentRepository
- [ ] Implement file upload service with 10MB limit and magic-byte validation
- [ ] Implement SHA-256 file hashing and duplicate detection per user
- [ ] Configure Spring `@Async` task executor for background processing
- [ ] Implement HTTP client to communicate with FastAPI internal endpoints (`AiEngineClient`)
- [ ] Implement async document processing pipeline: UPLOADED -> EXTRACTING -> ANALYZING -> COMPLETED/FAILED
- [ ] Implement document status polling endpoint (`GET /api/documents/{id}/status`)
- [ ] Write integration tests for upload, deduplication, and async status flow

### Phase 6: Spring Boot Backend — Analysis Persistence & Full-Text Search Retrieval
- [ ] Implement entities and repositories for DocumentAnalysis, ExtractedClause, RiskFinding, ExtractedInformation, MissingClauseWarning, and DocumentChunk
- [ ] Persist extraction results and verification metadata from AI engine
- [ ] Implement chunk storage with PostgreSQL tsvector and GIN index
- [ ] Implement full-text search chunk retrieval for question answering (`ChunkRetrievalService`)
- [ ] Implement ChatController and ChatMessage persistence with page citations
- [ ] Add endpoints for querying clauses, risks, key information, and missing clauses with filters
- [ ] Write integration tests for analysis retrieval and search-grounded chat

### Phase 7: Spring Boot Backend — OpenPDF Report Generation & Dashboard Statistics
- [ ] Implement DashboardService aggregating real database metrics (totals, risk breakdown, recent documents)
- [ ] Implement OpenPDF report generator covering all 10 standard report sections
- [ ] Include page citations and EXTRACTED / AI_INTERPRETATION provenance tags in PDF
- [ ] Implement ReportController (`GET /api/documents/{id}/report`)
- [ ] Implement DashboardController (`GET /api/dashboard/stats`)
- [ ] Write unit tests for report generation and dashboard metrics calculation

### Phase 8: Frontend — Project Setup, Auth, Layout & Document Upload
- [ ] Initialize React 18 + Vite project with Tailwind CSS and shadcn/ui components
- [ ] Configure color tokens (navy primary, neutral grays, semantic risk colors)
- [ ] Set up React Router, theme context (light/dark mode), and authentication context with JWT storage
- [ ] Build Landing, Login, and Register pages with restrained legal-tech styling
- [ ] Build Dashboard page displaying real statistics, risk charts, and recent documents
- [ ] Build Document Upload page with drag-and-drop, duplicate detection modal, file type validation, and upload consent notice
- [ ] Implement polling hook for document processing status with clear progress steps

### Phase 9: Frontend — Analysis Workspace, Side-by-Side Viewer & Grounded Chat
- [ ] Build Document Analysis workspace layout with tabbed navigation
- [ ] Implement Summary tab with document purpose, parties, and commercial conditions
- [ ] Implement Clauses tab with category/importance filters and 3 simplification modes (Simple, Detailed, Professional)
- [ ] Implement side-by-side Document Viewer showing cited page text when finding is clicked
- [ ] Implement Risks tab with risk severity badges and suggested questions
- [ ] Implement Key Information tab and Missing Clauses tab
- [ ] Implement Grounded Chat interface with clickable page citation pills
- [ ] Add PDF Report download button and document history page

### Phase 10: Evaluation Suite, End-to-End Testing & Viva Preparation
- [ ] Curate sample contracts in `samples/contracts/` (NDA, Lease, Service Agreement, Employment, Prompt Injection test)
- [ ] Build evaluation script (`evaluation/evaluate.py`) measuring extraction accuracy, quote verification rate, and response latency
- [ ] Run automated end-to-end test verifying full path: upload -> analyze -> poll -> inspect -> chat -> export
- [ ] Create documentation: `docs/architecture.md`, `docs/api-documentation.md`, `docs/privacy.md`
- [ ] Prepare viva examination documents in `docs/viva/` (frequently asked viva questions and demo script)
- [ ] Verify clean execution from a fresh environment according to README instructions
