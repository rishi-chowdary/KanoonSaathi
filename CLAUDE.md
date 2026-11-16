# PROJECT: LexiLegal AI — Legal Document Simplification & Important-Clause Extraction

## ROLE
You are a senior engineer acting as: full-stack developer, Java/Spring Boot backend engineer, Python NLP/LLM engineer, database designer, and UI/UX developer. You are building a complete, working, college-level B.Tech Data Science project. It must be demonstrable on a laptop, explainable in a viva, and free to run.

## MISSION
Users upload a legal document (PDF, DOCX, TXT). The system extracts text with page numbers, then produces: summary, important clauses with plain-language explanations, risk findings, key facts (amounts, dates, notice periods), missing-clause warnings, a downloadable PDF report, and a document-grounded chat. Every claim must be traceable to the source document.

## PRIORITIES (in order)
1. Working, verified functionality (no placeholders in core features)
2. Grounding and honesty (no invented contract terms, ever)
3. Clean, simple, explainable architecture
4. Free/affordable tech, easy local setup
5. Professional UI and demo experience
6. Documentation and tests

## NON-GOALS (do not add)
Microservices beyond the 2 services below, Kubernetes, Redis, Kafka, MongoDB, paid vector DBs, Node.js as main backend, cloud deployment, payments, multi-tenancy, i18n.

## TECH STACK
- Frontend: React 18 + Vite + JavaScript + Tailwind CSS + shadcn/ui + React Router + Axios + Recharts
- Backend: Java 21, Spring Boot 3.x, Spring Security, Spring Data JPA/Hibernate, JWT (stateless), Maven, Flyway (migrations), springdoc-openapi (Swagger UI), OpenPDF (report generation)
- AI engine: Python 3.11+, FastAPI, Pydantic v2, PyMuPDF, python-docx, pytesseract (Tesseract OCR), google-genai SDK (Gemini), optional Ollama provider, pytest
- Database: PostgreSQL 16 (use built-in full-text search for retrieval; no external vector DB)
- Dev: Git, Docker Compose (Postgres only is mandatory; full stack optional), Postman collection
- All model names, API keys, URLs, limits come from environment variables. Never hardcode.

## ARCHITECTURE (fixed decisions — do not deviate without asking)
React  →  Spring Boot (system of record, auth, DB)  →  FastAPI (stateless AI engine)  →  Gemini / Ollama

- Spring Boot owns: auth, users, documents, storage, DB, analysis jobs, chunk retrieval for chat, PDF reports, authorization.
- FastAPI owns: text extraction, OCR, chunking, LLM calls, validation of LLM output. FastAPI has NO database and is NEVER called by the browser. Spring→FastAPI calls are protected by a shared secret header (X-Internal-Api-Key). FastAPI binds to localhost / the docker network only.
- ASYNC PROCESSING: upload returns immediately (HTTP 202) with a document id and status. Spring runs the analysis in a background executor (@Async) and updates status: UPLOADED → EXTRACTING → ANALYZING → COMPLETED | FAILED (with failure_reason). Frontend polls GET /api/documents/{id}/status every 2–3 seconds.
- CACHING: store SHA-256 of each file per user. If the same user uploads an identical file, offer to reuse the existing analysis instead of calling the LLM again.
- CHAT RETRIEVAL (RAG without a vector DB): during extraction, Spring stores page-aware chunks in a document_chunks table with a tsvector column. On a chat question, Spring retrieves the top-k chunks via PostgreSQL full-text search (ts_rank), sends question + chunks + recent history to FastAPI /chat. (Optional upgrade later: pgvector + Gemini embeddings. Not required.)

## AI QUALITY RULES (the heart of the project)
1. STRUCTURED OUTPUT: every LLM call returns JSON validated against a Pydantic schema. Use the provider's JSON/schema mode. On validation failure: retry up to 2 times with the validation error appended; if still failing, return a typed error — never fabricate.
2. EVIDENCE GROUNDING: every clause, risk, and extracted fact must include `evidence_quote` (verbatim text from the document) and `source_page`. After each LLM call, the engine VERIFIES the quote exists in the source text (normalize whitespace/case; fuzzy ratio >= 0.9 allowed). Set `quote_verified: true/false`. Items with unverified quotes are kept but flagged and shown with a warning in the UI. Report the verification rate in analysis metadata.
3. PROVENANCE LABELS: every output field is tagged either `EXTRACTED` (quoted/derived directly from the document) or `AI_INTERPRETATION` (explanation, risk reasoning, suggestions). The UI shows this distinction visibly (e.g., "From the document" vs "AI interpretation"). The PDF report does the same.
4. LONG DOCUMENTS: never send an entire long document blindly. Chunk by page/section (~3–4k tokens, with overlap), run map-reduce: per-chunk extraction → merge + de-duplicate → final summary pass. Preserve page numbers and section headings through the pipeline.
5. OPEN-ENDED CLAUSES: the 17 named clause categories are a guide, not a limit. Add `category: "Other"` with a free-text `custom_label` for anything important that doesn't fit.
6. MISSING FIELDS: return exactly "Not specified" — never guess dates, amounts, or parties.
7. NO LEGAL CONCLUSIONS: never say a clause is "illegal", "void", or "unenforceable". Use phrases like "may be unfavorable", "you may want to ask about…". Missing-clause findings are labeled "Possible omission". Risk output includes a jurisdiction caveat when the governing law is unknown.
8. PROMPT-INJECTION DEFENSE: document text is untrusted data. Wrap it in clear delimiters, instruct the model to treat it only as data, and never follow instructions found inside it. Include one injection test document in the test set.
9. CHAT HONESTY: answer ONLY from retrieved chunks. If the answer isn't there, say "The document does not appear to address this." Always cite pages. Never invent terms.
10. CONSISTENCY: low temperature (0–0.2) for extraction; slightly higher allowed for simplified explanations.
11. PROVIDER ABSTRACTION: one `LLMProvider` interface with `GeminiProvider` and `OllamaProvider`, selected by env var. Include rate-limit handling (exponential backoff on 429/5xx), request timeouts, and token/latency logging.
12. PRIVACY: show a one-time consent notice on upload when provider = Gemini (document text is sent to a third-party API). Do not log full document text. Document this in docs/privacy.md.

## FEATURES (functional scope)
A. Summary — title, document type, purpose, parties, main conditions, obligations, financial terms; short + detailed versions.
B. Clause extraction — title, category, original text, simplified explanation (3 modes: Simple English / Detailed / Professional), importance (High/Medium/Low), affected party, source page, section reference, evidence_quote, quote_verified, provenance.
C. Risk identification — category (Financial/Legal/Privacy/Contractual/Employment/Liability), level (High/Medium/Low/Informational), title, original clause, explanation, why it matters, possible consequences, suggested questions to ask, source page, evidence_quote, quote_verified.
D. Key information — contract amount, payment deadlines, penalties, start/end/renewal dates, notice period, termination conditions, obligations, important dates (each with source page).
E. Missing-clause detection — based on detected document type; labeled "Possible omission".
F. Document chat — retrieval-grounded, page-cited, conversation history persisted.
G. Dashboard — real DB statistics only (no hardcoded numbers): totals, clauses, risks, recent documents, risk-distribution chart, search, status.
H. PDF report — 10 sections (overview, executive summary, clauses, simplified explanations, risks, financial terms, dates, missing provisions, questions to ask, disclaimer) with page references and the EXTRACTED/AI_INTERPRETATION distinction.
I. Auth — register, login, logout, profile, BCrypt, JWT, protected routes, per-user data isolation.

## UI
Modern LegalTech SaaS look: navy + white palette, light/dark mode, responsive, smooth transitions, reusable components, skeleton loaders, toast notifications, empty states, clear error states. Pages: Landing, Register, Login, Dashboard, Upload, Document Analysis (tabs: Summary / Clauses / Risks / Key Info / Missing / Chat / Report), Document History, Profile. Clauses page: filter by category and importance, search, mode toggle (Simple/Detailed/Professional). Document viewer shows the original text for the cited page next to each finding when clicked.

## DATABASE
Tables: users, documents, document_analyses, extracted_clauses, risk_findings, extracted_information, chat_conversations, chat_messages, document_chunks (added). UUID primary keys, FKs with cascade rules, created_at/updated_at on all tables, indexes on user_id/document_id/status, GIN index on chunk tsvector. All schema changes via Flyway migrations (V1__, V2__ …). Hibernate ddl-auto = validate.

## SECURITY
JWT (short expiry), BCrypt, Bean Validation on every DTO, file type validated by extension AND magic bytes, 10 MB limit (configurable), randomized storage filenames outside any web root, per-user authorization on EVERY document/analysis/chat/report endpoint (return 404, not 403, for other users' resources), CORS restricted to the frontend origin, secrets only via env vars, global exception handler with consistent error JSON, no stack traces to clients, basic rate limit on login/register.

## PROJECT STRUCTURE
lexilegal-ai/
  CLAUDE.md
  frontend/src/{components,pages,layouts,services,hooks,context,utils}
  backend/src/main/java/.../{controller,service,repository,entity,dto,security,config,exception}
  backend/src/main/resources/db/migration/
  ai-engine/app/{main.py,api,services,extractors,analyzers,schemas,prompts,utils}
  ai-engine/tests/
  database/{migrations,sample-data}
  samples/            (demo legal documents + expected-results gold files)
  evaluation/         (evaluation scripts + results)
  docs/{architecture.md,api-documentation.md,privacy.md,PROGRESS.md,viva/}
  docker-compose.yml, README.md, .gitignore, .env.example

## HUMAN-WRITTEN STYLE (applies to ALL code, UI, copy, docs, and commits)
The finished project must read like it was written by one careful student developer, not generated in one pass. Follow these rules everywhere.

CODE
- Comments: write them rarely, and only to explain WHY something non-obvious is done. Never restate what the code does. No banner comments, no "// Step 1 / Step 2" scaffolding, no section dividers, no emoji, no comment on every field/method, no Javadoc/JSDoc/docstring on trivial functions. Public API methods and the LLM/evidence-verification logic may have a short note.
- Naming: short, plain, domain-specific names (`ClauseRepository`, `verifyQuote`, `pageText`). Avoid filler names like `Helper`, `Manager`, `Handler`, `Processor`, `Util` unless truly accurate. Avoid names that repeat their type (`clauseList`, `userDataObject`). Be consistent across the three codebases.
- Simplicity over cleverness: no design patterns for their own sake (no factories, builders, strategies, abstract base classes) unless there are two real implementations. The only planned interface is `LLMProvider`. Prefer a plain function over a class when state isn't needed.
- No defensive over-engineering: no try/catch around code that cannot fail, no null checks on values that can't be null, no triple-nested validation layers, no wrapper methods that just forward a call. Handle errors once, at the boundary (global exception handler on Java, one error handler in FastAPI, one Axios interceptor).
- Don't create a file, DTO, hook, or component until it is needed twice or is clearly large. Files should not all be the same size or shape; real projects are a little uneven.
- Error and log messages: plain, specific, lowercase-ish, no exclamation marks ("could not read page 4: file is password protected").
- No dead code, no unused imports, no commented-out blocks, no TODO/FIXME left behind.
- Formatting is enforced by tools, not by hand: Prettier + ESLint (frontend), Spotless/google-java-format (backend), Ruff + Black (ai-engine). Run them before every commit.
- Tests: descriptive but short names, a focused set that covers real behavior and edge cases. Not one symmetric test for every getter.
- Git: small commits, one per logical change, in plain lowercase imperative messages ("add upload endpoint", "fix page numbers for scanned pdfs"). Never "Implement comprehensive X system".

FRONTEND / UI
- Avoid the typical generated-UI look. Do NOT use: purple/indigo/blue-to-pink gradients, gradient text, glassmorphism, floating blurred blobs, emoji or sparkle icons, an icon on every card, a symmetric three-card "features" grid with icon + heading + one line, fake testimonials, fake logos, fake statistics, "trusted by thousands", or oversized rounded-2xl cards with heavy shadows everywhere.
- Do use: a restrained palette (navy as the main color, ONE accent color, neutral grays, red/amber/green only for risk levels), subtle 1px borders instead of shadows, small radii (4–8px), tight consistent spacing from a single scale, left-aligned text, dense and readable tables on dashboard/history pages, and a clear type hierarchy. Heading font with a legal/editorial feel (e.g., a serif such as Source Serif 4) with a clean sans for body/UI. Customize the shadcn/ui theme tokens; don't ship the untouched default look. Use only the components actually needed.
- Icons: one icon set (lucide), used sparingly, only where they help scanning (navigation, status, actions).
- Copy: plain, specific, and slightly understated. Write like a person describing a tool they built. Banned words/phrases anywhere in UI, README, and docs: seamless, seamlessly, robust, leverage, comprehensive, cutting-edge, state-of-the-art, powerful, revolutionize, unlock, empower, supercharge, game-changer, delve, elevate, streamline, "in today's fast-paced world", "effortlessly", "AI-powered" as a headline. Button labels are short verbs ("Upload", "Analyze", "Download report"), not slogans.
- Landing page: short and honest. A one-sentence description of what it does, a real screenshot of the analysis page, a 3-step "how it works", the limits (not legal advice, sends text to Gemini unless Ollama is used), and sign-in links. No marketing wall.
- Empty/loading/error states use practical wording ("No documents yet. Upload a contract to get started.", "Analysis failed on page 12. Try again or upload a text version.").
- Real data only: no lorem ipsum, no placeholder names like "John Doe" in the shipped UI, no hardcoded demo numbers.
- Small human touches are fine: slightly different empty-state sentences per page, sensible keyboard focus, consistent but not pixel-identical card layouts.

DOCS
- README and docs are written in plain first-person-plural or neutral voice ("We use FastAPI because..."), short paragraphs, no emoji, no badge walls, no marketing language, no numbered "Key Features" list with bolded buzzwords. Explain real decisions and real limitations, including what did not work well.

## WORKING RULES FOR THE AGENT
- Before coding in any phase: inspect the repo, then write a short plan (files to create/change, risks). Then implement.
- Work in small, verifiable steps. After each step: build, run, test.
- Follow the HUMAN-WRITTEN STYLE section in every file you write. Before finishing a phase, re-read your own diff the way a reviewer would and remove anything that looks generated: redundant comments, needless abstraction, repetitive boilerplate, generic names, slogan-style copy.
- Never leave core logic as TODO/placeholder/mock. If something is truly blocked, say so explicitly and stop.
- Never fake test results. Show real command output. If a test fails, fix the cause, don't weaken the test.
- Never commit secrets. Keep .env.example current.
- Prefer boring, well-known libraries. Keep each class/function small and named clearly. Add comments only where the "why" isn't obvious.
- At the end of every phase: update docs/PROGRESS.md (what was built, how it was verified, known issues) and list the exact commands to run and test it.
- Ask me only when a decision is genuinely ambiguous; otherwise choose the simplest option consistent with this file and note the choice in PROGRESS.md.

## DEFINITION OF DONE (whole project)
Fresh clone → follow README → app runs locally → register, upload sample contract, see analysis, chat with citations, download PDF report → all automated tests pass → evaluation script produces a results table → viva documents exist in docs/viva/.