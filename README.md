# LexiLegal AI — Legal Contract Simplification & Clause Extraction

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![MySQL 8](https://img.shields.io/badge/database-MySQL%208-orange.svg)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero External APIs](https://img.shields.io/badge/APIs-100%25%20Offline%20Local%20NLP-brightgreen.svg)](#privacy--security-guarantees)

**LexiLegal AI** is an enterprise-grade legal document analysis and plain-language simplification platform built with a pure, transparent, local Python Natural Language Processing (NLP) stack. It transforms complex legal contracts (leases, NDAs, employment agreements, vendor contracts, promissory notes) into verified clause inventories, grounded risk assessments, key factual summaries, and downloadable 10-section PDF legal dossiers.

Every extracted finding, evidence quote, and risk factor is strictly anchored to verifiable character offsets in the original document with exact page citations.

---

## 🏛️ Architectural Overview

LexiLegal AI operates as a unified, monolithic Flask application with clear separation between routing blueprints, service layers, and core NLP engines:

```
lexilegal-ai/
├── app/
│   ├── __init__.py               # Flask application factory, error handlers, extensions
│   ├── config.py                 # Configuration loader reading .env
│   ├── models/                   # SQLAlchemy ORM models (User, Document, Clause, Risk, etc.)
│   ├── blueprints/               # Thin route controllers (auth, documents, studio, main)
│   ├── services/                 # Business logic (document, clause, risk, chat, report, dashboard)
│   ├── nlp/                      # Pure Python NLP engine package
│   │   ├── extraction.py         # PyMuPDF per-page extraction + Tesseract OCR fallback
│   │   ├── segmentation.py       # Legal punkt sentence & clause boundary segmentation
│   │   ├── clause_classifier.py  # Ensemble classifier (DistilBERT LEDGAR + SBERT + Rules)
│   │   ├── document_classifier.py# Document type categorization (embeddings + rules)
│   │   ├── summarizer.py         # Extractive summarization (SBERT TextRank + MMR)
│   │   ├── simplifier.py         # Tri-Tier plain language simplifier (Simple, Detailed, Pro)
│   │   ├── readability.py        # Pure-Python Flesch Reading Ease & Kincaid Grade Level
│   │   ├── key_info.py           # Entity extraction with font-dropped symbol repair
│   │   ├── risk_engine.py        # Grounded contract risk detection + Rule 7 guardrails
│   │   ├── missing_provisions.py # Document-type expected checklist evaluation
│   │   ├── retrieval.py          # Hybrid passage retrieval (SBERT dense + BM25 sparse RRF)
│   │   ├── qa_engine.py          # Extractive QA (minilm-squad2) + Fact Intent Router
│   │   └── registry.py           # Single-point offline model lifecycle registry
│   ├── templates/                # Server-rendered Jinja2 templates (semantic HTML5)
│   └── static/                   # Hand-written CSS, vanilla JavaScript, local static Chart.js
├── data/                         # Knowledge bases (glossary, risk rules, expected provisions)
├── evaluation/                   # Offline evaluation suite, benchmark runner, gold files, RESULTS.md
├── migrations/                   # Alembic database schema migrations
├── samples/                      # Curated test contracts & ground truth gold annotations
├── scripts/                      # Utility scripts (download_models.py, smoke_test.sh)
├── tests/                        # 94 automated pytest unit, integration & parity tests
├── docker-compose.yml            # Containerized MySQL 8 (InnoDB, utf8mb4)
├── requirements.txt              # Pinned Python dependencies
└── run_local.sh                  # One-command local startup script
```

---

## ⚡ Key Invariants & NLP Methodology

1. **Exact Source Slice Invariant (100% Quote Verification)**:
   Every clause text, summary sentence, and risk quote is guaranteed to be an exact substring slice of the original text with verifiable `[start_offset:end_offset]` character positions. No generative hallucinations or altered wording.
2. **Rule 6 Absent Field Integrity**:
   When contractual terms (such as penalties, renewal terms, or end dates) are omitted from a document, the system strictly outputs `"Not specified"`. Zero invented dates or amounts.
3. **Rule 7 Legal Advice Guard**:
   The system strictly avoids definitive legal conclusions (*"illegal"*, *"void"*, *"unenforceable"*, *"unlawful"*). All advisory commentary uses calibrated non-definitive phrasing (*"may create ambiguity"*, *"presents significant financial exposure"*, *"questionable under standard commercial practice"*). Missing provisions are labeled `"Possible omission"`.
4. **SQuAD 2.0 Honest Refusal Invariant**:
   For questions outside the document scope, the extractive QA model measures candidate logit delta against the unanswerable null token ($\Delta = \text{best\_span\_score} - \text{null\_score} < 0.0$). Unanswerable queries reliably trigger honest refusal: `"The document does not appear to address this."` with zero fabricated citations.

---

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **MySQL**: 8.0 or higher (InnoDB engine, `utf8mb4` character set)
- **Tesseract OCR**: (Optional, for scanned document OCR)
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr tesseract-ocr-eng`
  - Fedora/RHEL: `sudo dnf install tesseract tesseract-langpack-eng`
  - macOS: `brew install tesseract`

---

## 🚀 Quick Start (One Command)

To launch the complete application with automated database verification and migration:

```bash
chmod +x run_local.sh
./run_local.sh
```

The application will be accessible at: **`http://127.0.0.1:5000`**.

---

## 🛠️ Step-by-Step Manual Setup

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/lexilegal-ai.git
cd lexilegal-ai

python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
Edit `.env` to configure your MySQL connection details and application secret key:
```ini
FLASK_ENV=development
SECRET_KEY=lexilegal_secure_session_secret_key_change_in_production
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=lexilegal
MYSQL_USER=lexilegal
MYSQL_PASSWORD=lexilegal
SQLALCHEMY_DATABASE_URI=mysql+pymysql://lexilegal:lexilegal@127.0.0.1:3306/lexilegal?charset=utf8mb4
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=10485760
```

### 3. Start MySQL Database (Docker or Native)
Using Docker Compose:
```bash
docker compose up -d
```
Or connect to your existing local MySQL 8 instance.

### 4. Download NLP Models (Offline Cache)
Pre-download the offline SBERT, DistilBERT, spaCy, and Extractive QA models:
```bash
python scripts/download_models.py
```

### 5. Apply Database Migrations
```bash
flask db upgrade
```

### 6. Run Application Server
```bash
python run.py
```

---

## 🧪 Testing & Verification Suite

### 1. Full Pytest Test Suite (94 Tests, 85% Coverage)
```bash
.venv/bin/pytest tests/ --cov=app -q
```
Runs comprehensive automated tests covering:
- Ingestion, magic byte validation, Tesseract OCR fallback, and character slice invariants
- DistilBERT LEDGAR ensemble clause classification and importance scoring
- Grounded risk detection rules, predatory clause identification, and Rule 7 compliance
- Entity extraction, font-dropped symbol repair, and SBERT TextRank summarization
- Tri-tier simplification and Flesch reading ease score calculations
- Hybrid passage retrieval (SBERT + BM25 RRF) and extractive QA with honest refusal
- Multi-user SQL dashboard metrics, document deletion cascade, and tenant isolation
- 10-section ReportLab PDF dossier generation with running headers and TrueType Unicode fonts

### 2. Offline Benchmark Runner & Evaluation Suite
```bash
.venv/bin/python evaluation/evaluate_nlp_stack.py
```
Executes offline evaluation across all gold standard contract fixtures and outputs a detailed Markdown report to `evaluation/RESULTS.md`.

### 3. End-to-End Smoke Test Script
```bash
./scripts/smoke_test.sh
```
Executes the full user workflow over live HTTP endpoints:
`Register User` $\rightarrow$ `Upload Contract` $\rightarrow$ `Verify Clauses` $\rightarrow$ `Verify Risks` $\rightarrow$ `Interactive Grounded Q&A` $\rightarrow$ `Download 10-Section PDF Report`.

### 4. Code Quality & Format Checks
```bash
.venv/bin/ruff check app tests evaluation/evaluate_nlp_stack.py
.venv/bin/black --check app tests evaluation/evaluate_nlp_stack.py
```

---

## 📊 Benchmark Results (Old LLM vs. New Local NLP Stack)

| Metric | Target Standard | Legacy Gemini API | New Local Python NLP | Result |
|---|---|---|---|---|
| **Clause Recall** | $\ge 80.0\%$ | 100.0% | **100.0%** (14/14) | **PASS** |
| **Clause Precision** | $\ge 75.0\%$ | 100.0% | **85.7%** (14/16) | **PASS** |
| **Quote Verification Rate** | $\ge 85.0\%$ | 91.2% | **100.0%** | **EXCEEDS** |
| **Risk Detection Recall** | $\ge 70.0\%$ | 92.3% | **100.0%** (10/10) | **PASS** |
| **Predatory Clause Traps** | 100% on one-sided | 3/3 Detected | **3/3 Detected** | **PASS** |
| **Rule 7 Forbidden Claims** | Exactly 0 | 0 | **0** | **STRICT PASS** |
| **Rule 6 "Not specified" Accuracy** | 100% | 100.0% | **100.0%** | **PASS** |
| **Chat Answer Accuracy** | $\ge 80.0\%$ | 100.0% | **100.0%** (10/10) | **PASS** |
| **Citation Page Accuracy** | $\ge 80.0\%$ | 100.0% | **100.0%** (10/10) | **PASS** |
| **Honest Refusal Rate** | $\ge 80.0\%$ | 100.0% | **100.0%** (5/5) | **PASS** |
| **Average Pipeline Latency** | $< 30.0\text{s}$ | 12.40s | **0.48s** | **~25.9x Faster** |
| **Average Interactive Chat Latency**| $< 5.0\text{s}$ | 1.80s | **~0.12s** | **~15.0x Faster** |
| **Cloud Tokens / Contract** | Budget $\le 10,000$ | ~7,480 tokens | **0 tokens** | **OPTIMAL** |
| **Cloud Cost / Contract** | Budget $\le \$0.01$ | ~$0.00042 | **$0.00 (Zero)** | **OPTIMAL** |

*Detailed benchmark tables, per-contract metrics, and analysis latency breakdowns are documented in [evaluation/RESULTS.md](file:///home/rishichowdary/Documents/lexilegal-ai/evaluation/RESULTS.md).*

---

## 🔒 Privacy & Security Guarantees

1. **100% On-Premise Execution**:
   All NLP extraction, summarization, classification, and question answering execute locally in PyTorch/Python processes. Document text never leaves the host server.
2. **Tenant Isolation**:
   All database queries filter strictly on `user_id == current_user.id`. Cross-user access attempts return HTTP 404 (preventing user enumeration).
3. **Session Security & CSRF Protection**:
   Session cookies use `HttpOnly`, `SameSite=Lax`, and CSRF protection via Flask-WTF on all web form submissions.
4. **File Safety**:
   Uploaded files undergo strict magic-byte validation (PDF `%PDF`, DOCX `PK\x03\x04`), 10MB size limits, and SHA-256 duplicate content detection.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
