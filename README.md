# LexiLegal AI

LexiLegal AI is a local web application for reading and reviewing legal contracts. You upload a PDF, DOCX, or plain text file and it extracts the text page by page, breaks the contract into clauses, highlights risk patterns, pulls out key dates and amounts, rewrites clauses in simpler English, and lets you ask questions about the document.

Everything runs locally in Python on your machine. No document text is sent to any external API or hosted model.

## What it does

- **Text extraction and OCR**: Reads PDFs with PyMuPDF, Word files with `python-docx`, and plain text files directly. Scanned PDF pages with very little text fall back to Tesseract OCR.
- **Clause extraction and classification**: Splits contracts on headings and sentence boundaries, then classifies each clause across 17 categories (such as Payment Terms, Termination, Confidentiality, and Indemnity) using an ensemble of a LEDGAR DistilBERT model, sentence-transformer prototypes, and keyword rules.
- **Plain-language simplification**: Rewrites clauses using three rule-based modes (`simple`, `detailed`, and `professional`) backed by a 151-term legal glossary, sentence splitting, and Flesch readability scores. Also available standalone at `/studio`.
- **Key facts and summaries**: Extracts parties, amounts, deadlines, late fees, dates, and notice periods using spaCy NER, regex patterns, and `dateparser`. Produces an extractive summary using SBERT TextRank with Maximal Marginal Relevance (MMR).
- **Risk flags and missing provisions**: Matches clauses against YAML risk rules and semantic prototypes, then compares the document against a per-contract-type checklist to note possible omissions.
- **Document Q&A**: Uses hybrid retrieval (SBERT dense embeddings plus BM25 merged with Reciprocal Rank Fusion), a deterministic fact matcher, and `deepset/minilm-uncased-squad2` extractive QA. When the score falls below the unanswerable threshold, it replies: `"The document does not appear to address this."`
- **PDF report export**: Builds a 10-section PDF report with ReportLab using local TrueType fonts so currency symbols (`$`, `₹`) and section marks (`§`) render cleanly.

## Project layout

```text
lexilegal-ai/
├── app/
│   ├── __init__.py               # Flask app factory, error handlers, startup recovery
│   ├── config.py                 # Environment configuration (.env)
│   ├── extensions.py             # SQLAlchemy, Migrate, LoginManager, CSRF, Limiter
│   ├── models/                   # 10 SQLAlchemy tables
│   ├── blueprints/               # Thin route modules (auth, documents, analysis, chat, reports, studio, main)
│   ├── services/                 # Document, clause, analysis, risk, chat, dashboard, report services
│   ├── nlp/                      # Local NLP pipeline
│   │   ├── extraction.py         # PyMuPDF, python-docx, Tesseract OCR
│   │   ├── segmentation.py       # Heading regex + legal-abbreviation-aware NLTK punkt
│   │   ├── clause_classifier.py  # LEDGAR DistilBERT + SBERT + keyword rules
│   │   ├── document_classifier.py
│   │   ├── key_info.py           # Amounts, dates, notice periods, parties
│   │   ├── summarizer.py         # SBERT TextRank + MMR extractive summary
│   │   ├── simplification/       # Glossary, rewriter, templates, trap checks
│   │   ├── readability.py        # Pure-Python Flesch Reading Ease and Kincaid Grade
│   │   ├── risk_engine.py        # YAML rules, prototypes, legal claim filter
│   │   ├── missing_provisions.py # Document-type expected checklists
│   │   ├── retrieval.py          # SBERT + BM25 Reciprocal Rank Fusion
│   │   ├── qa_engine.py          # Fact intent router + minilm-uncased-squad2
│   │   └── registry.py           # Thread-safe lazy model loader
│   ├── templates/                # Jinja2 HTML templates
│   └── static/                   # Hand-written CSS, vanilla JS, local fonts, local Chart.js
├── data/                         # YAML glossary, risk rules, prototypes, expected checklists
├── evaluation/                   # Offline benchmark script, gold fixtures, RESULTS.md
├── migrations/                   # Alembic migrations
├── samples/                      # Sample contracts and gold annotations
├── scripts/                      # download_models.py, snapshot.py, smoke_test.sh, style_check.py
├── tests/                        # 95 pytest tests
├── docker-compose.yml            # MySQL 8 container
├── requirements.txt
└── run_local.sh                  # Local startup script
```

## Prerequisites

- Python 3.11 or newer
- MySQL 8.0 or newer (`InnoDB`, `utf8mb4`)
- Tesseract OCR (optional, only needed for scanned PDFs):
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr tesseract-ocr-eng`
  - Fedora/RHEL: `sudo dnf install tesseract tesseract-langpack-eng`
  - macOS: `brew install tesseract`

## Quick start

```bash
chmod +x run_local.sh
./run_local.sh
```

Then open `http://127.0.0.1:5000` in your browser.

## Manual setup

1. Create a virtual environment and install dependencies:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your MySQL settings:
   ```bash
   cp .env.example .env
   ```
3. Start MySQL (either locally or with Docker):
   ```bash
   docker compose up -d
   ```
4. Pre-download the local NLP models:
   ```bash
   python scripts/download_models.py
   ```
5. Run database migrations and start the server:
   ```bash
   flask db upgrade
   python run.py
   ```

## Tests and evaluation

Run the test suite with coverage:
```bash
.venv/bin/pytest tests/ --cov=app -q
```

Run the offline benchmark on the gold sample contracts (updates `evaluation/RESULTS.md`):
```bash
.venv/bin/python evaluation/evaluate_nlp_stack.py
```

Run the live HTTP smoke test against a running server:
```bash
./scripts/smoke_test.sh
```

Run lint, formatting, and style checks:
```bash
.venv/bin/ruff check app tests scripts evaluation/evaluate_nlp_stack.py
.venv/bin/black --check app tests scripts evaluation/evaluate_nlp_stack.py
.venv/bin/python scripts/style_check.py
```

### Benchmark summary

Measured on the project's gold sample contracts (`evaluation/RESULTS.md`):

| Metric | Local NLP stack | Notes |
|---|---|---|
| Clause recall | 100.0% (14/14) | On the annotated gold set |
| Clause precision | 85.7% (14/16) | Two extra clauses flagged on gold set |
| Quote offset match rate | 100.0% | Verifies offset slicing (`text[start:end]`), not model judgment |
| Risk recall | 100.0% (10/10) | Including 3/3 predatory traps on `one_sided_agreement.pdf` |
| Absent fields defaulting to `"Not specified"` | 100.0% | Zero invented dates or amounts |
| Chat answer accuracy | 100.0% (10/10) | On `evaluation/chat_questions.json` |
| Chat refusal on unanswerable questions | 100.0% (5/5) | Returns `"The document does not appear to address this."` |
| Average pipeline latency | ~0.5s per contract | Local CPU after models are loaded |

## Limitations

It is worth being direct about what this tool does not do well:

- **Not legal advice**: Every risk note and suggestion is informational only. The risk filter softens absolute legal claims (such as "illegal", "void", or "unenforceable") into non-definitive wording, and missing checks are marked `"Possible omission"`.
- **Rule-based simplification is less fluent than a generative LLM**: Replacing legal phrases from a glossary and splitting long sentences keeps numbers, dates, and negations intact, but the rewritten prose can sound mechanical on dense multi-clause paragraphs.
- **Domain gap on Indian contracts**: The LEDGAR DistilBERT model was trained on US SEC filings (EDGAR). Keyword rules and SBERT prototypes help bridge Indian rental, employment, and service agreements, but unusual local phrasing can still fall back to `Other`.
- **What "100% quote verification" means**: The quote verification metric checks that every stored excerpt is an exact character slice of the extracted document text. It guarantees quotes are not altered or fabricated; it does not mean a clause category or risk flag is guaranteed legally correct.
- **DOCX page numbers are approximate**: Word `.docx` files do not store rendered page breaks reliably without a full layout engine, so page numbers on DOCX uploads are estimated from character counts.
- **English only**: The spaCy model, glossary, risk rules, and QA model only support English contracts.

## Documentation

- [System architecture](docs/architecture.md)
- [REST API reference](docs/api-documentation.md)
- [Privacy and data handling](docs/privacy.md)
- [5-minute demo walkthrough](docs/DEMO.md)
- [Migration notes (old prototype to local Python stack)](docs/MIGRATION_NOTES.md)

## License

MIT — see [LICENSE](LICENSE).
