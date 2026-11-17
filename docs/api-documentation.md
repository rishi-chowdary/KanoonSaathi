# LexiLegal AI — REST API Documentation

This document describes all client-facing REST API endpoints provided by the LexiLegal AI Python application.

- **Base URL**: `http://127.0.0.1:5000`
- **Authentication**: Session cookie (`session`) managed via Flask-Login (obtained via `/api/auth/login` or `/api/auth/register`)
- **CSRF Protection**: Web UI forms require Flask-WTF CSRF tokens; programmatic JSON APIs under `/api/*` are exempted for automated and headless test client integration.

---

## 1. Authentication & User Profile

### `POST /api/auth/register`
Registers a new user account, initializes the session, and returns user details.
- **Request Body**:
  ```json
  {
    "email": "counsel@example.com",
    "password": "SecurePassword123!",
    "full_name": "Sarah Connor"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "counsel@example.com",
    "full_name": "Sarah Connor",
    "role": "USER",
    "created_at": "2026-11-17T20:00:00Z"
  }
  ```
- **Error Codes**: `400 Bad Request` (email already exists, password < 8 characters).

---

### `POST /api/auth/login`
Authenticates user credentials and establishes an active session cookie. Rate-limited to prevent brute-force attacks.
- **Request Body**:
  ```json
  {
    "email": "counsel@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "Login successful",
    "user": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "counsel@example.com",
      "full_name": "Sarah Connor",
      "role": "USER"
    }
  }
  ```
- **Error Codes**: `401 Unauthorized` (invalid email or password).

---

### `POST /api/auth/logout`
Terminates the current session and clears cookies.
- **Response**: `200 OK`
  ```json
  {
    "message": "Logout successful"
  }
  ```

---

### `GET /api/auth/profile`
Returns metadata and statistics for the currently authenticated user.
- **Response**: `200 OK`
  ```json
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "counsel@example.com",
    "full_name": "Sarah Connor",
    "role": "USER",
    "created_at": "2026-11-17T20:00:00Z"
  }
  ```

---

## 2. Document Ingestion & Pipeline

### `POST /api/documents/upload`
Uploads and ingests a contract document (PDF, DOCX, or TXT, up to 10MB). Automatically runs layout-aware extraction, OCR if required, clause segmentation, and entity extraction.
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `file`: binary file payload
- **Response**: `201 Created`
  ```json
  {
    "id": "7b84494a-8742-45e3-8208-d6e245a44365",
    "originalFilename": "rental_agreement.pdf",
    "fileType": "PDF",
    "fileSize": 2649,
    "pageCount": 2,
    "status": "COMPLETED",
    "createdAt": "2026-11-17T20:05:00Z"
  }
  ```
- **Error Codes**: `400 Bad Request` (duplicate file upload, file > 10MB, corrupted file, unsupported extension).

---

### `GET /api/documents`
Lists all documents uploaded by the current user, ordered newest first.
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "7b84494a-8742-45e3-8208-d6e245a44365",
      "originalFilename": "rental_agreement.pdf",
      "fileType": "PDF",
      "fileSize": 2649,
      "pageCount": 2,
      "status": "COMPLETED",
      "createdAt": "2026-11-17T20:05:00Z"
    }
  ]
  ```

---

### `GET /api/documents/<id>`
Retrieves full metadata and processing status for a single document.
- **Response**: `200 OK` (Document object)
- **Error Codes**: `404 Not Found` (document does not exist or belongs to another user).

---

### `GET /api/documents/<id>/status`
Lightweight polling endpoint to inspect extraction status.
- **Response**: `200 OK`
  ```json
  {
    "id": "7b84494a-8742-45e3-8208-d6e245a44365",
    "status": "COMPLETED",
    "pageCount": 2,
    "failureReason": null
  }
  ```

---

### `GET /api/documents/<id>/text`
Returns the extracted raw text partitioned by page number.
- **Response**: `200 OK`
  ```json
  {
    "documentId": "7b84494a-8742-45e3-8208-d6e245a44365",
    "pageCount": 2,
    "pages": [
      {
        "pageNumber": 1,
        "text": "RESIDENTIAL LEASE AGREEMENT..."
      },
      {
        "pageNumber": 2,
        "text": "Section 5. Maintenance..."
      }
    ]
  }
  ```

---

### `DELETE /api/documents/<id>`
Permanently deletes the document, its physical storage, and all associated clauses, chunks, risks, and conversations.
- **Response**: `200 OK`
  ```json
  {
    "message": "Document deleted successfully"
  }
  ```

---

## 3. Clause Analysis & Grounded Risks

### `GET /api/documents/<id>/clauses`
Retrieves classified clauses for the document with optional category and importance filters.
- **Query Parameters**:
  - `category` (optional, e.g. `Payment Terms`, `Termination`, `Liability`)
  - `importance` (optional: `HIGH`, `MEDIUM`, `LOW`)
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "c1a2b3c4-...",
      "title": "Section 2. Monthly Rent and Payment Terms",
      "category": "Payment Terms",
      "sectionReference": "Section 2",
      "originalText": "Tenant agrees to pay Landlord a monthly rent of $2,400.00...",
      "importance": "HIGH",
      "evidenceQuote": "monthly rent of $2,400.00, payable in advance on or before the first",
      "quoteVerified": true,
      "sourcePage": 1,
      "clauseIndex": 2,
      "simplified": {
        "simple": "Tenant pays $2,400.00 monthly rent on the first of each month.",
        "detailed": "...",
        "professional": "..."
      }
    }
  ]
  ```

---

### `GET /api/documents/<id>/risks`
Returns all contractual risk findings grounded directly in verified source text.
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "r1a2b3...",
      "ruleId": "FIN_SEVERE_LATE_FEE",
      "category": "Financial",
      "level": "HIGH",
      "title": "Severe Late Charges and Accelerated Administrative Fees",
      "explanation": "The payment window is unusually short, and late interest accrues at an elevated rate...",
      "whyItMatters": "Even minor administrative delays could cause penalties and interest to compound rapidly.",
      "possibleConsequences": "Substantial unexpected financial liabilities accumulating quickly.",
      "suggestedQuestions": [
        "Can the payment grace period be extended to 30 days?"
      ],
      "sourcePage": 1,
      "evidenceQuote": "Late interest shall accrue at 2.5% per month, compounded daily",
      "quoteVerified": true
    }
  ]
  ```

---

### `GET /api/documents/<id>/missing-provisions`
Returns missing standard provisions evaluated against the document type checklist.
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "m1a2b3...",
      "clauseName": "Carve-outs from Confidential Information",
      "riskLevel": "HIGH",
      "whyItMatters": "Without explicit carve-outs for public domain or independently developed information...",
      "label": "Possible omission"
    }
  ]
  ```

---

### `GET /api/documents/<id>/risk-distribution`
Aggregated counts of risks grouped by severity level and category for Chart.js rendering.
- **Response**: `200 OK`
  ```json
  {
    "byLevel": {
      "HIGH": 3,
      "MEDIUM": 2,
      "LOW": 1
    },
    "byCategory": {
      "Financial": 2,
      "Liability": 2,
      "Contractual": 2
    }
  }
  ```

---

## 4. Grounded Document Chat (Extractive Q&A)

### `POST /api/documents/<id>/chat`
Submits a user question about the document and returns a grounded extractive answer with page citations.
- **Request Body**:
  ```json
  {
    "message": "What is the monthly rent and when is it due?",
    "conversation_id": null
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "conversationId": "chat-uuid-1234",
    "messageId": "msg-uuid-5678",
    "role": "ASSISTANT",
    "answer": "The specified contract/payment amount is $2,400.00. Payment schedule/deadline: on or before the first (1st) day of each calendar month.",
    "citations": [
      {
        "page": 1,
        "sectionRef": "Page 1",
        "quote": "$2,400.00",
        "quoteVerified": true
      }
    ],
    "addressedInDocument": true,
    "confidence": 1.0,
    "createdAt": "2026-11-17T20:10:00Z"
  }
  ```

---

### `GET /api/documents/<id>/chat/conversations`
Lists all conversation threads for this document.
- **Response**: `200 OK` (Array of conversation objects)

---

### `GET /api/documents/<id>/chat/conversations/<conversation_id>/messages`
Retrieves multi-turn message history for a specific conversation thread.
- **Response**: `200 OK` (Array of user/assistant message objects with citations)

---

### `DELETE /api/documents/<id>/chat/conversations/<conversation_id>`
Deletes a conversation thread and its message history.
- **Response**: `200 OK` `{"message": "Conversation deleted successfully"}`

---

## 5. ReportLab PDF Dossier & Dashboard

### `GET /api/documents/<id>/report`
Generates and downloads the formal 10-section ReportLab PDF Legal Dossier.
- **Response Headers**:
  - `Content-Type: application/pdf`
  - `Content-Disposition: attachment; filename="<filename>_Analysis_Report.pdf"`
- **Response**: Raw PDF binary stream.

---

### `GET /documents/<id>/report.pdf`
Streams the 10-section ReportLab PDF directly to the browser for inline preview.
- **Response Headers**:
  - `Content-Type: application/pdf`
  - `Content-Disposition: inline; filename="<filename>_Analysis_Report.pdf"`

---

### `GET /api/dashboard/stats`
Computes real SQL aggregate metrics filtered strictly on `current_user.id` (zero hardcoded numbers).
- **Response**: `200 OK`
  ```json
  {
    "totalDocuments": 3,
    "analyzedDocuments": 3,
    "failedDocuments": 0,
    "totalClauses": 24,
    "totalRisks": 7,
    "averageVerificationRate": 100.0,
    "riskDistributionByLevel": {
      "HIGH": 3,
      "MEDIUM": 3,
      "LOW": 1
    },
    "riskDistributionByCategory": {
      "Liability": 3,
      "Contractual": 2,
      "Financial": 2
    }
  }
  ```
