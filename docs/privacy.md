# LexiLegal AI — Privacy & Data Governance Architecture

## 1. Core Commitment & Legaltech Privacy Model

**LexiLegal AI** is architected specifically for sensitive legal contracts, non-disclosure agreements, and confidential corporate documents. Following its migration to a pure local Python NLP stack, LexiLegal AI guarantees **100% on-premise data residency**, eliminating cloud data transmission risks entirely.

---

## 2. Zero-Cloud Processing & Local NLP Invariants

### 2.1 Complete Local Processing (Zero External API Calls)
- **Zero Cloud Transmission**: All natural language processing tasks—including document layout extraction, optical character recognition (OCR), ensemble clause classification, extractive summarization, risk detection, and question answering—run strictly in-process on the local host.
- **No Third-Party Models or APIs**: The system uses zero hosted AI services (no Gemini, no OpenAI, no Anthropic, no Ollama). Document contents, contract terms, and user questions never leave your server.
- **Model Storage**: Pre-trained model weights (DistilBERT LEDGAR, SBERT `all-MiniLM-L6-v2`, `deepset/minilm-uncased-squad2`, and spaCy `en_core_web_md`) reside entirely on the local filesystem.

### 2.2 Inference Telemetry & Logging Safeguards
- Raw contract text and user queries are completely stripped from application telemetry and persistent logging.
- Error logs and server logs record only document UUIDs, timestamp metrics, and high-level execution statuses, never verbatim contract excerpts or sensitive client data.

---

## 3. Data Storage & Multi-Tenant Isolation

### 3.1 Data at Rest & Encryption
- **Physical Document Storage**: Uploaded binary documents (PDF, DOCX, TXT) are stored in partitioned user subdirectories (`./uploads/<user_id>/`) with UUID-based path masking to prevent filesystem traversal.
- **Database Persistence**: Structured analyses, extracted clauses, risk findings, key metadata, and conversation logs are persisted in MySQL 8 (InnoDB, `utf8mb4`).
- **Strict Tenant Isolation**: Every database read, update, and delete query is parameterized with `user_id == current_user.id`. Requests attempting to access documents belonging to other users return an opaque `404 Not Found` response, eliminating document existence enumeration.

### 3.2 Right to Erasure & Immediate Deletion
- When a document is deleted via the web interface or `DELETE /api/documents/<id>`:
  1. The underlying physical contract file is immediately unlinked and removed from disk.
  2. The `documents` row is deleted, triggering cascade deletion across `document_analyses`, `extracted_clauses`, `risk_findings`, `extracted_information`, `missing_clause_warnings`, `document_chunks`, `chat_conversations`, and `chat_messages`.
  3. No residual metadata, cached embeddings, or orphaned records remain in the database.

---

## 4. Regulatory Notice & Rule 7 Legal Advice Guard

LexiLegal AI provides automated NLP information extraction, plain-language simplification, and contract risk highlighting. **It does not provide formal legal advice, legal counsel representation, or statutory compliance guarantees.**

To protect users against the unauthorized practice of law (UPL):
- The platform strictly enforces **Rule 7 Legal Advice Guards**, eliminating conclusionary legal statements (*"illegal"*, *"void"*, *"unenforceable"*, *"unlawful"*).
- All advisory commentary employs calibrated non-definitive phrasing (*"may create ambiguity"*, *"presents significant financial exposure"*, *"questionable under standard commercial practice"*).
- Missing standard provisions are labeled `"Possible omission"` rather than legal defects.
