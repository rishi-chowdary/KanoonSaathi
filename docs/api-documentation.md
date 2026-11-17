# REST API Reference

All JSON API endpoints live under `/api/*` on the Flask server (`http://127.0.0.1:5000` by default).

- **Authentication**: Session cookie (`session`) set by Flask-Login after calling `POST /api/auth/login` or `POST /api/auth/register`.
- **CSRF**: Web HTML forms require a Flask-WTF CSRF token. JSON endpoints under `/api/*` are exempt for API clients and tests.
- **User isolation**: Any document endpoint returns `404 Not Found` if the ID does not exist or belongs to another user.

## 1. Authentication

### `POST /api/auth/register`
Creates an account and starts a logged-in session.
- **Body**: `{"email": "user@example.com", "password": "Password123!", "full_name": "Jane Doe"}`
- **Success**: `201 Created` with user object (`id`, `email`, `full_name`, `role`, `created_at`).
- **Errors**: `400 Bad Request` (duplicate email, missing fields, password shorter than 8 characters).

### `POST /api/auth/login`
Verifies email and password and sets the session cookie. Rate-limited.
- **Body**: `{"email": "user@example.com", "password": "Password123!"}`
- **Success**: `200 OK` with `{"message": "Login successful", "user": {...}}`.
- **Errors**: `401 Unauthorized` on invalid credentials.

### `POST /api/auth/logout`
Clears the current session.
- **Success**: `200 OK` with `{"message": "Logout successful"}`.

### `GET /api/auth/profile`
Returns profile fields for the logged-in user.
- **Success**: `200 OK` with `id`, `email`, `full_name`, `role`, `created_at`.

## 2. Documents

### `POST /api/documents/upload`
Uploads a PDF, DOCX, or TXT file (max 10 MB), validates extension and magic bytes, checks for a duplicate SHA-256 hash for this user, extracts text, and runs the NLP analysis pipeline.
- **Content-Type**: `multipart/form-data` with field `file`.
- **Success**: `201 Created` with document metadata (`id`, `originalFilename`, `fileType`, `fileSize`, `pageCount`, `status`, `createdAt`).
- **Errors**: `400 Bad Request` (unsupported format, invalid magic bytes, empty/corrupted/encrypted file, duplicate upload).

### `GET /api/documents`
Lists documents owned by the logged-in user, newest first.
- **Success**: `200 OK` with JSON array of document objects.

### `GET /api/documents/<doc_id>`
Returns metadata and status for a single document.
- **Success**: `200 OK` with document object.

### `GET /api/documents/<doc_id>/status`
Returns current processing status (`id`, `status`, `pageCount`, `failureReason`).

### `GET /api/documents/<doc_id>/text`
Returns extracted text chunks with page numbers (`documentId`, `pageCount`, `pages`).

### `DELETE /api/documents/<doc_id>`
Deletes the uploaded file from disk and cascades deletion across analyses, clauses, risks, key info, chunks, and chat conversations.
- **Success**: `200 OK` with `{"message": "Document deleted successfully"}`.

## 3. Analysis, clauses, and risks

### `GET /api/documents/<doc_id>/clauses`
Returns extracted clauses for the document.
- **Optional query params**: `category` (e.g. `Payment Terms`, `Termination`), `importance` (`HIGH`, `MEDIUM`, `LOW`).
- **Response fields per clause**: `id`, `title`, `category`, `sectionReference`, `originalText`, `importance`, `evidenceQuote`, `quoteVerified`, `sourcePage`, `clauseIndex`, and `simplified` (`simple`, `detailed`, `professional`).

### `GET /api/documents/<doc_id>/key-info`
Returns extracted financial terms, dates, notice periods, termination conditions, and obligations. Fields absent from the contract return `"Not specified"`.

### `GET /api/documents/<doc_id>/summary`
Returns the extractive short and detailed summaries, document type, purpose, and detected parties.

### `GET /api/documents/<doc_id>/risks`
Returns detected risk findings (`id`, `ruleId`, `category`, `level`, `title`, `explanation`, `whyItMatters`, `possibleConsequences`, `suggestedQuestions`, `sourcePage`, `evidenceQuote`, `quoteVerified`).

### `GET /api/documents/<doc_id>/missing-provisions`
Returns expected clauses not found in the document, each tagged with `"label": "Possible omission"`.

### `GET /api/documents/<doc_id>/risk-distribution`
Returns counts grouped by `byLevel` (`HIGH`, `MEDIUM`, `LOW`) and `byCategory` for Chart.js.

## 4. Document Q&A

### `POST /api/documents/<doc_id>/chat`
Answers a question from the document's extracted facts and text chunks.
- **Body**: `{"message": "What is the monthly rent?", "conversation_id": null}`
- **Success**: `200 OK` with `id`, `conversationId`, `role`, `content`, `citations` (page number, section reference, quote, `quoteVerified`), `addressedInDocument`, and `createdAt`.
- When no passage meets the confidence threshold, `addressedInDocument` is `false` and `content` is `"The document does not appear to address this."`.

### `GET /api/documents/<doc_id>/chat/conversations`
Lists conversation threads for the document.

### `GET /api/documents/<doc_id>/chat/conversations/<conversation_id>/messages`
Returns ordered messages and citations for a conversation.

### `DELETE /api/documents/<doc_id>/chat/conversations/<conversation_id>`
Deletes a conversation thread and its messages.

## 5. Simplification studio

### `POST /api/simplify`
Simplifies an arbitrary legal clause without uploading a full document.
- **Body**: `{"text": "...", "mode": "simple_english", "category": "INDEMNITY", "affected_party": "Tenant"}`
- **Success**: `200 OK` with `simple`, `detailed`, `professional`, Flesch readability scores before and after, matched glossary terms, and trap warnings.

### `GET /api/glossary`
Returns the local Indian and general legal glossary entries from `data/glossary.yaml`.

### `GET /api/statutes`
Searches offline BNS 2023 <-> IPC 1860 sections and Constitution of India articles.
- **Query params**: `q` (section number, article number, or keyword), `type` (`all`, `bns`, `ipc`, `constitution`).

### `POST /api/issue-helper`
Matches an everyday plain-English description of a legal problem to possible Indian legal provisions (BNS/IPC, Constitution, Negotiable Instruments Act, IT Act, Consumer Protection Act, Labour/Tenancy/Contract laws).
- **Body**: `{"issue": "Someone took Rs. 50,000 promising a job via UPI and blocked my number."}`
- **Success**: `200 OK` with `matched`, `summary`, `disclaimer`, and `suggestions` (`citation`, `title`, `category`, `relevance`, `plainEnglish`, `details`, `whereToFile`, `nextSteps`, `excerpt`).

## 6. Reports and dashboard

### `GET /api/documents/<doc_id>/report`
Downloads the 10-section PDF report (`Content-Type: application/pdf`, `Content-Disposition: attachment`).

### `GET /documents/<doc_id>/report.pdf`
Streams the same PDF report inline for browser preview (`Content-Disposition: inline`).

### `GET /api/dashboard/stats`
Returns per-user SQL aggregates: `totalDocuments`, `analyzedDocuments`, `failedDocuments`, `totalClauses`, `totalRisks`, `averageVerificationRate`, `riskDistributionByLevel`, and `riskDistributionByCategory`.
