# Privacy and Data Handling

KanoonSaathi runs completely on the machine where you host it. Contract text, extracted clauses, and user questions stay inside your local Flask process and MySQL database.

## Local processing

- **No external API calls**: Text extraction, OCR, clause classification, summarization, simplification, risk checks, and document Q&A all run locally in Python. There are no calls to Gemini, OpenAI, Anthropic, or any hosted model API.
- **Local model weights**: The spaCy pipeline (`en_core_web_md`), sentence-transformer (`all-MiniLM-L6-v2`), extractive QA model (`deepset/minilm-uncased-squad2`), and LEDGAR classifier are downloaded once via `scripts/download_models.py` and loaded from local disk after that.
- **No external frontend assets**: Fonts, stylesheets, JavaScript, and Chart.js are served from `app/static/`.

## Logging

Application logs record document IDs, status transitions, and failure reasons (for example, password-protected or corrupted files). Full contract text and user chat messages are never written to logs.

## Storage and user isolation

- **Uploaded files**: Saved under `./uploads/<user_id>/` using generated UUID filenames rather than raw user-supplied paths.
- **Database**: Structured analysis outputs live in MySQL 8 (`InnoDB`, `utf8mb4`).
- **Per-user isolation**: Every document, analysis, report, and chat query checks `Document.user_id == current_user.id`. Requests for another user's document ID return HTTP `404` instead of `403` so document IDs cannot be probed across accounts.
- **Session and form security**: Flask-Login sets `HttpOnly` and `SameSite=Lax` session cookies, passwords use Werkzeug scrypt hashing, and HTML forms enforce Flask-WTF CSRF tokens.

## Deletion

Deleting a document (from the web UI or via `DELETE /api/documents/<id>`) removes:

1. The uploaded file on disk.
2. The `documents` row and, via foreign-key cascades, its `document_analyses`, `extracted_clauses`, `risk_findings`, `extracted_information`, `missing_clause_warnings`, `document_chunks`, `chat_conversations`, and `chat_messages` rows.

## Legal notice

KanoonSaathi is a student NLP project for reading and summarizing contract text. It does not provide legal advice or determine whether a clause is valid or enforceable in any jurisdiction. Risk descriptions avoid absolute legal conclusions, and missing-provision items are labeled `"Possible omission"`.
