# LexiLegal AI — Privacy & Data Governance Architecture

## 1. Core Commitment & Legaltech Privacy Model

LexiLegal AI is designed specifically for sensitive legal contracts, NDAs, and corporate agreements. It adheres to strict data privacy principles to ensure confidentiality, integrity, and regulatory compliance.

---

## 2. Data Transmission & LLM Boundaries

### 2.1 Inference Data Boundary
- **Transmission**: When using external inference providers (such as Google Gemini API via `gemini-3.5-flash-lite`), only extracted chunk text and structured analysis prompts are transmitted over encrypted TLS 1.3 channels.
- **Zero Training Commitment**: Under enterprise API terms, data transmitted through the Gemini API is **not** used to train foundation models, train fine-tuned models, or improve Google products.
- **Local / Mock Mode Support**: LexiLegal AI supports offline execution (`USE_MOCK_LLM=true`), ensuring that in sensitive or isolated environments, zero bytes leave the local infrastructure.

### 2.2 Inference Logging Safeguards
- Raw document text is stripped from application telemetry and log files.
- Exception handlers and server logs log only document identifiers and anonymized token metrics, never verbatim contract excerpts.

---

## 3. Data Storage & Multi-Tenant Isolation

### 3.1 Data at Rest
- **Document Files**: Uploaded binary documents (PDF, DOCX, TXT) are stored in the local server directory (`./uploads`) with UUID-based path masking to prevent filesystem enumeration.
- **Database Persistence**: Structured analyses, extracted clauses, risks, key dates, and chunks are stored in PostgreSQL with strict foreign-key cascade deletion.
- **Tenant Isolation**: Every database operation is scoped to the authenticated `user_id`. Access to documents belonging to other users returns an opaque `404 Not Found` response to prevent existence enumeration.

### 3.2 Right to Erasure / Deletion Guarantees
- When a user deletes a document via `DELETE /api/documents/{id}`:
  1. The binary file is immediately unlinked and deleted from storage.
  2. The `documents` record is deleted, triggering an automated database `ON DELETE CASCADE` across `document_analyses`, `extracted_clauses`, `risk_findings`, `extracted_information`, `missing_clause_warnings`, `document_chunks`, and `chat_conversations`.
  3. No residual metadata or vectors remain in the database.

---

## 4. Legal Disclaimer & Regulatory Notice

LexiLegal AI provides automated information extraction, natural-language summarization, and commercial risk identification. **It does not provide formal legal advice, legal representation, or statutory compliance guarantees.** The platform should be used to support and inform human review by qualified legal counsel.
