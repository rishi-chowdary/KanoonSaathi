# LexiLegal AI — API Documentation

This document describes all REST API endpoints provided by the LexiLegal AI platform, including the client-facing Spring Boot application (`/api/*`) and internal AI Engine microservices (`/internal/*`).

- **Base URL**: `http://localhost:8080/api`
- **Authentication**: Bearer JWT in `Authorization: Bearer <token>` header
- **Internal Service Auth**: `X-Internal-Api-Key: <internal_key>` header

---

## 1. Authentication & User Profile

### `POST /api/auth/register`
Creates a new user account and returns an authentication JWT token.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "Password123!",
    "fullName": "Jane Doe"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
    "user": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "user@example.com",
      "fullName": "Jane Doe",
      "role": "USER",
      "createdAt": "2026-11-17T12:00:00Z"
    }
  }
  ```

### `POST /api/auth/login`
Authenticates existing credentials and returns a JWT token. Rate limited to 5 attempts per minute per IP.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "Password123!"
  }
  ```
- **Response**: `200 OK` (AuthResponse with token and user object)

### `GET /api/auth/profile` (or `GET /api/users/me`)
Retrieves the profile of the currently authenticated user.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` (UserProfileResponse)

---

## 2. Document Ingestion & Pipeline

### `POST /api/documents/upload`
Uploads a legal contract in PDF, DOCX, or TXT format (max 10MB). Magic byte inspection and SHA-256 deduplication are enforced.
- **Headers**: `Authorization: Bearer <token>`
- **Content-Type**: `multipart/form-data`
- **Form Data**: `file` (binary document)
- **Response**: `202 Accepted`
  ```json
  {
    "id": "7681629e-c871-466a-8d1b-5bf627c01eb2",
    "originalFilename": "rental_agreement.pdf",
    "status": "UPLOADED",
    "fileSize": 2649,
    "pageCount": 0,
    "isDuplicate": false,
    "createdAt": "2026-11-17T12:00:00Z"
  }
  ```

### `GET /api/documents/{id}/status`
Returns the real-time processing status of the document.
- **Response**: `200 OK`
  ```json
  {
    "id": "7681629e-c871-466a-8d1b-5bf627c01eb2",
    "status": "COMPLETED",
    "failureReason": null,
    "pageCount": 3,
    "isScanned": false
  }
  ```
  *Possible Status Values*: `UPLOADED`, `EXTRACTING`, `EXTRACTED`, `ANALYZING`, `COMPLETED`, `COMPLETED_WITH_WARNINGS`, `FAILED`.

### `GET /api/documents/{id}/text`
Retrieves extracted plain text for a document, with optional page filtering.
- **Query Parameters**: `page` (optional integer, 1-indexed)
- **Response**: `200 OK`
  ```json
  {
    "documentId": "7681629e-c871-466a-8d1b-5bf627c01eb2",
    "page": 1,
    "totalPages": 3,
    "text": "RESIDENTIAL LEASE AGREEMENT\nThis Lease Agreement..."
  }
  ```

### `POST /api/documents/{id}/reanalyze`
Re-runs the multi-stage analysis pipeline using stored chunks.
- **Response**: `202 Accepted`
  ```json
  {
    "status": "ANALYZING",
    "message": "Document reanalysis triggered successfully"
  }
  ```

### `DELETE /api/documents/{id}`
Deletes a document and cascades deletion across all analyses, clauses, risks, chunks, and chat messages.
- **Response**: `204 No Content`

---

## 3. Analysis Results & Clauses

### `GET /api/documents/{id}/analysis`
Returns the executive summary, parties, purpose, obligations, and verification rate.
- **Response**: `200 OK` (AnalysisSummaryResponse)

### `GET /api/documents/{id}/clauses`
Returns paginated clauses with tri-tier plain English simplifications and verified quotes.
- **Query Parameters**: `category`, `importance` (`HIGH`, `MEDIUM`, `LOW`), `search`, `page`, `size`
- **Response**: `200 OK`
  ```json
  {
    "content": [
      {
        "id": "clause-uuid",
        "title": "Early Termination",
        "category": "Termination",
        "simplifiedSimple": "You must give 30 days notice to end the lease early.",
        "simplifiedDetailed": "Detailed breakdown...",
        "simplifiedProfessional": "Commercial summary...",
        "importance": "HIGH",
        "sourcePage": 2,
        "evidenceQuote": "Either party may terminate upon thirty (30) days notice.",
        "quoteVerified": true
      }
    ],
    "totalElements": 7,
    "totalPages": 1,
    "number": 0
  }
  ```

### `GET /api/documents/{id}/risks`
Returns identified legal and financial risks, color-coded severity, and suggested negotiation questions.
- **Query Parameters**: `level` (`HIGH`, `MEDIUM`, `LOW`), `category`
- **Response**: `200 OK` (List of RiskFindingResponse)

### `GET /api/documents/{id}/key-info`
Returns structured key terms (financial amounts, dates, notice periods, deadlines). Unspecified fields strictly return `"Not specified"`.
- **Response**: `200 OK` (KeyInformationResponse)

### `GET /api/documents/{id}/missing`
Returns missing provisions identified by comparing the contract against curated document-type checklists. All items are labeled `"Possible omission"` with disclaimer text.
- **Response**: `200 OK` (List of MissingClauseWarningResponse)

### `POST /api/documents/{id}/clauses/{clauseId}/re-explain`
Dynamically re-explains a clause on demand in a requested explanation style (`simple_english`, `detailed`, `professional`).
- **Response**: `200 OK` (ReExplainClauseResponse)

---

## 4. Grounded RAG Chat

### `POST /api/documents/{id}/chat`
Sends a question about the document. Answers are strictly grounded in retrieved chunks with structured citations.
- **Request Body**:
  ```json
  {
    "conversationId": "optional-uuid",
    "message": "What is the penalty for late rent payments?"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "conversationId": "uuid",
    "messageId": "uuid",
    "role": "assistant",
    "content": "A late fee of 5% applies if rent is not received by the 5th day of the calendar month.",
    "citations": [
      {
        "page": 2,
        "sectionRef": "Section 4. Late Fees",
        "quote": "If rent is not received by the 5th, a late fee of 5% of the monthly rent shall be assessed.",
        "quoteVerified": true
      }
    ],
    "confidence": "supported",
    "createdAt": "2026-11-17T12:00:00Z"
  }
  ```

### `GET /api/documents/{id}/chat/conversations`
Lists all chat conversations for this document and current user.
- **Response**: `200 OK` (List of ChatConversationResponse)

### `GET /api/documents/{id}/chat/conversations/{conversationId}/messages`
Retrieves chronological message history with citations.
- **Response**: `200 OK` (List of ChatMessageResponse)

### `DELETE /api/documents/{id}/chat/conversations/{conversationId}`
Deletes a chat thread and all associated messages.
- **Response**: `204 No Content`

---

## 5. Dashboard & Reports

### `GET /api/dashboard/stats`
Computes real-time SQL aggregates for the current user (no cross-tenant leakage).
- **Response**: `200 OK`
  ```json
  {
    "totalDocuments": 3,
    "analyzedDocuments": 3,
    "failedDocuments": 0,
    "totalClauses": 21,
    "totalRisks": 7,
    "riskDistributionByLevel": {
      "HIGH": 2,
      "MEDIUM": 4,
      "LOW": 1,
      "INFORMATIONAL": 0
    },
    "riskDistributionByCategory": {
      "Liability": 3,
      "Termination": 2,
      "Financial": 2
    },
    "recentDocuments": [...],
    "recentAnalyses": [...]
  }
  ```

### `GET /api/documents/{id}/report.pdf`
Generates a downloadable 10-section OpenPDF report dossier with running headers/footers, page numbers, and TrueType Unicode font rendering.
- **Response**: `200 OK` (`Content-Type: application/pdf`, `Content-Disposition: inline; filename="lexilegal_report_{id}.pdf"`)

---

## 6. Simplification Studio

### `POST /api/simplify`
Simplifies arbitrary legal text snippets without requiring document upload.
- **Request Body**:
  ```json
  {
    "text": "The Lessee shall indemnify and hold harmless the Lessor...",
    "mode": "simple_english",
    "documentContext": "Commercial Lease"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "mode": "simple_english",
    "explanation": "You promise to pay for any damage or legal claims made against the landlord.",
    "glossary": [
      {
        "term": "Indemnify",
        "plainDefinition": "To protect or compensate someone for legal harm or financial loss."
      }
    ],
    "warningPoints": [
      "This shifts significant financial liability onto you."
    ]
  }
  ```

---

## 7. AI Engine Internal Endpoints (Port 8000)

*Protected by `X-Internal-Api-Key` header.*

| Endpoint | Method | Description |
|---|---|---|
| `/internal/health` | `GET` | Health check and provider connectivity status |
| `/internal/extract` | `POST` | Multipart PDF/DOCX page and chunk extraction |
| `/internal/analyze/summary` | `POST` | Executive summary, parties, and purpose analysis |
| `/internal/analyze/clauses` | `POST` | Clause boundary detection, tri-tier simplifications, quote verification |
| `/internal/analyze/risks` | `POST` | Risk detection with Rule 7 conclusion filtering |
| `/internal/analyze/key-info` | `POST` | Key facts, dates, amounts, and deadline extraction |
| `/internal/analyze/missing` | `POST` | Checklist comparison for missing standard provisions |
| `/internal/chat` | `POST` | Grounded RAG question answering with verbatim citations |
| `/internal/simplify` | `POST` | Standalone text simplification and glossary mapping |
