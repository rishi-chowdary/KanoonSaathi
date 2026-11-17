# LexiLegal AI — College Project Seminar Presentation

---

## Slide 1 — Title Slide

**Title:** LexiLegal AI — Local Indian Legal Document Analysis & Plain-Language Simplification  
**Subtitle:** Extracting Important Clauses, Key Information, Risk Flags, and Plain-English Legal Guidance Offline  
**Footer:** B.Tech Data Science Project Seminar | Team Members | Roll Numbers | Guide Name | Department

**Speaker Notes:**  
Introduce LexiLegal AI as an offline web application built to help ordinary Indian users without legal training understand contracts, Bharatiya Nyaya Sanhita (BNS 2023) sections, IPC sections, Constitutional articles, and everyday legal issues.

---

## Slide 2 — Problem Statement

**Problem Statement:**  
*"Analyze legal documents, extract important clauses and key information, and convert complex legal language into simpler and more understandable summaries."*

**Why this problem matters in India:**
- Everyday agreements (rental / leave-and-license agreements, employment offer letters, bonds, service contracts, promissory notes) are written in dense legal wording.
- Non-lawyers frequently miss hidden risks such as uncapped liability, steep compounding late fees, short eviction windows, or unfair auto-renewal traps.
- With India's transition from **IPC (1860)** to **BNS (2023)**, citizens struggle to interpret statutory sections or know which legal provisions apply when facing real-world issues (online/UPI scams, bounced cheques, unpaid salary, landlord deposit disputes, or unlawful detention).
- Sending sensitive legal documents to external online services raises **privacy**, **hallucination**, and **cost** concerns.

**Speaker Notes:**  
Focus on the real gap: legal literacy in India is a barrier for ordinary people, and routine document review should be private, fast, and easy to understand.

---

## Slide 3 — What Is LexiLegal AI?

A **100% local, privacy-first Python NLP web application** designed for Indian legal documents and everyday citizens.

**Three Core Workflows:**
1. **Document Analyzer (`/upload` -> `/documents/<id>`):** Upload any PDF, DOCX, TXT, or scanned PDF (OCR) to get a plain-language summary, categorized clauses, key rupee/date facts, risk alerts, detected BNS/IPC/Constitutional references, page-cited Q&A, and a downloadable 10-section PDF report.
2. **Simplification Studio & BNS/IPC Lookup (`/studio`):** Paste any BNS section, IPC section, Constitutional article, or contract clause to rewrite it in 3 modes (**Simple English**, **Detailed**, **Professional**) with before/after Flesch readability scores, a 200+ term legal glossary, and an offline BNS <-> IPC / Constitution reference table.
3. **Indian Legal Issue Helper (`/helper`):** Type a real-life problem in plain everyday words (e.g., UPI job scam, cheque bounce, unpaid salary, landlord holding deposit) to get matching BNS/IPC, Constitutional, or civil/consumer provisions, where complaints are generally filed, and practical next steps.

**Speaker Notes:**  
Emphasize that a citizen does not need to know legal terminology to use the app — they can either upload a document or simply describe what happened in their own words.

---

## Slide 4 — Core Problems & How We Solved Them

| Technical Problem | How We Solved It |
|---|---|
| **1. Misquoting / Hallucinating Contract Text** | **Exact Character-Offset Slicing:** Every extracted clause and quote is verified directly as `full_text[start:end]` with exact page numbers (`100%` offset match). |
| **2. Privacy & External API Dependency** | **100% Local Python NLP:** PyMuPDF, Tesseract OCR, spaCy, NLTK, SBERT (`all-MiniLM-L6-v2`), DistilBERT, and `minilm-uncased-squad2` run locally on CPU with `0` external API calls and `₹0` runtime cost. |
| **3. Guessing Missing Dates or Amounts** | **Strict Absent-Field Default:** Whenever a field (such as penalties or renewal date) is absent from a contract, the extractor strictly returns `"Not specified"` (`0` invented values). |
| **4. Risk of Giving Unauthorized Legal Advice** | **Non-Definitive Wording Filter (`soften_legal_claims`):** Removes absolute legal verdicts (*"illegal"*, *"void"*, *"unenforceable"*); labels missing checks as `"Possible omission"` with clear disclaimers and NALSA helpline (`15100`). |
| **5. Unanswerable Q&A Queries** | **SQuAD 2.0 Refusal Threshold:** Compares best span score against the unanswerable null logit (`span_score - null_score < 0.0`) and honestly replies *"The document does not appear to address this."* |
| **6. Scanned PDFs & Indian Formatting** | **OCR + Indian Pattern Engineering:** Added Tesseract OCR fallback, PyMuPDF `INFINITE_RECT()` right-margin fix, Indian 2-digit comma rupee parsing (`₹18,00,000`), alphanumeric Indian sections (`Article 21A`, `Section 498A`), and Carlito Unicode fonts so `₹` renders and extracts cleanly. |

**Speaker Notes:**  
Highlight how each design choice prioritizes accuracy, transparency, and privacy over black-box generation.

---

## Slide 5 — Key Upgrades Built Into the System

1. **Upgraded from Generic Contract Extraction to Full Indian Legal Coverage**
   - Built an offline knowledge base (`data/indian_statutes.yaml`) covering **28 major BNS 2023 <-> IPC 1860 criminal sections**, **15 Constitution of India articles**, and **10 everyday civil & special laws** (Negotiable Instruments Act Sec. 138, IT Act Sec. 66C/66D, Consumer Protection Act 2019, Domestic Violence Act 2005, Indian Contract Act Sec. 27 & 73, Rent/Tenancy laws, Payment of Wages / Labour laws, RTI Act 2005, Motor Vehicles Act Sec. 166).
   - Added automatic BNS/IPC/Constitutional citation detection inside uploaded documents and Studio text.
2. **Upgraded with the Citizen Legal Issue Helper (`/helper`)**
   - Combines **SBERT semantic embeddings** and **everyday Indian scenario cues** so non-lawyers can type issues in plain English and get relevant sections, filing forums (Police FIR, Cybercrime 1930, Consumer e-Daakhil, Labour Samadhan, High Court Writ), and honest refusal on unrelated queries.
3. **Upgraded Simplification & Readability Engine**
   - Modularized into `app/nlp/simplification/` with a **200+ term Indian & general legal glossary**, Indian statutory phrasing rewrites (imprisonment terms, fines, constitutional restrictions, provisos), trap detection, preservation verification (numbers/dates/negations intact), and pure-Python Flesch Reading Ease scoring.
4. **Upgraded Engineering Quality, Security & UI**
   - Split routes into thin Flask blueprints (`documents`, `analysis`, `chat`, `reports`, `studio`, `auth`, `main`) with strict per-user isolation (`404` on cross-user access), CSRF protection, and scrypt password hashing.
   - Rebuilt the frontend with hand-written responsive CSS (light/dark mode, local fonts, local Chart.js, **0 horizontal overflow issues** across desktop, tablet, and mobile) and **106 automated pytest tests (88% code coverage)**.

**Speaker Notes:**  
Show examiners that every subsystem — NLP, Indian law coverage, security, UI responsiveness, and automated testing — was iteratively upgraded and verified.

---

## Slide 6 — System Architecture

```text
Browser UI (Jinja2 Templates, Hand-Written Responsive CSS, Vanilla JS, Local Chart.js)
                                      |
                                      v
          Flask Web Server & Thin Blueprints (Port 5000)
          |-- auth (Flask-Login sessions, CSRF, scrypt, rate limiter)
          |-- documents / analysis / chat / reports (per-user 404 isolation)
          +-- studio (Clause Simplifier, BNS/IPC Lookup, Legal Issue Helper)
                                      |
                                      v
       Service Layer (document, clause, analysis, risk, chat, report, dashboard)
                                      |
              +-----------------------+-----------------------+
              v                                               v
   Local Python NLP Pipeline (app/nlp/)            MySQL 8 (10 InnoDB Tables)
   - Extraction & OCR (PyMuPDF, DOCX, Tesseract)   + Local Uploads (./uploads/)
   - Segmentation (Indian Heading Regex + Punkt)   + Offline YAML Knowledge Bases
   - Ensemble Clause Classifier (22 categories)      - indian_statutes.yaml
   - Key Info & TextRank + MMR Summary               - glossary.yaml (200+ terms)
   - 3-Mode Simplifier & Flesch Readability          - clause_rules.yaml
   - Risk Engine & Missing-Provisions Check          - risk_rules.yaml
   - Hybrid QA (SBERT + BM25 RRF + MiniLM-SQuAD2)    - expected_provisions.yaml
   - Citizen Issue Matcher (SBERT + Scenario Cues)
```

**Speaker Notes:**  
Emphasize that everything runs inside a single clean Python application backed by MySQL 8, with thread-safe lazy model loading via `app/nlp/registry.py`.

---

## Slide 7 — End-to-End NLP Processing Pipeline

1. **Ingestion & Safety Checks:** Extension check (`.pdf`, `.docx`, `.txt`), magic-byte validation (`%PDF`, `PK\x03\x04`), 10 MB cap, SHA-256 duplicate detection, and automatic OCR for scanned pages.
2. **Segmentation & Classification:** Detects Indian statutory and contract headings (`Section 318`, `Article 21A`, numbered clauses), preserves exact character offsets, and classifies into 22 categories with importance levels (`HIGH` / `MEDIUM` / `LOW`).
3. **Summary & Key Information:** Generates an extractive executive summary (SBERT TextRank + MMR) plus a plain-language simplified summary, and extracts parties, `₹` amounts, payment schedules, dates, notice periods, and late penalties.
4. **Risk & Omission Analysis:** Flags high-risk traps (uncapped indemnity, compounding interest, unilateral modification, disproportionate caps) and checks expected provisions by contract type (skipping commercial checks on statutory documents like BNS/Constitution).
5. **Interactive Q&A & PDF Report:** Hybrid SBERT + BM25 retrieval merged with Reciprocal Rank Fusion (`k=60`) feeds `minilm-uncased-squad2` for page-cited answers; ReportLab exports a 10-section PDF report with Unicode `₹` and `§` support.

**Speaker Notes:**  
Point out the clear provenance badges across the UI (`From the document`, `Rule-based`, `Model prediction`, `Offline reference lookup`), so users can always distinguish verbatim document text from automated analysis.

---

## Slide 8 — Practical Uses & Who Benefits

- **General Citizens (No Law Background):** Describe an everyday dispute (UPI fraud, bounced cheque, unpaid salary, landlord deposit refusal, wrongful arrest) and immediately understand relevant Indian laws, helplines (`1930`, `112`, `1915`, `15100`), and next steps.
- **Tenants & Property Buyers:** Review Indian rental / leave-and-license agreements and scanned sale deeds before signing to spot hidden deductions, eviction notice periods, and missing refund clauses.
- **Employees & Job Seekers:** Inspect offer letters and employment bonds to understand non-compete clauses (Indian Contract Act Sec. 27), notice periods, and IP ownership terms.
- **Small Businesses & Freelancers:** Review client/vendor service contracts for uncapped indemnities, compounding late charges, and auto-renewal traps.
- **Law Students, Paralegals & Legal-Aid Clinics:** Fast offline BNS 2023 <-> IPC 1860 lookup, Constitutional article simplification, and printable 10-section analysis reports without uploading confidential files to third-party servers.

**Speaker Notes:**  
Connect directly to accessibility and social impact — helping citizens ask informed questions before signing documents or consulting a lawyer.

---

## Slide 9 — Evaluation & Test Results

*Verified offline with `evaluation/evaluate_nlp_stack.py` and `pytest tests/ --cov=app` on Indian sample contracts & statutes:*

| Metric | Target | Achieved | Result |
|---|---:|---:|---|
| Clause Extraction Recall | >= 80.0% | **100.0%** | PASS |
| Clause Extraction Precision | >= 75.0% | **85.7%** | PASS |
| Exact Quote Offset Match Rate | >= 85.0% | **100.0%** | PASS |
| Risk Detection Recall / Precision / F1 | >= 70.0% | **100.0% / 100.0% / 1.000** | PASS |
| One-Sided Contract Traps Detected | 3 / 3 | **3 / 3** | PASS |
| Disallowed Legal Conclusions | 0 | **0** | PASS |
| Absent Fields Defaulting to `"Not specified"` | 100% | **100.0% (0 invented)** | PASS |
| Document Q&A Answerable Accuracy | >= 80.0% | **90.0% (9/10)** | PASS |
| Document Q&A Unanswerable Refusal Rate | >= 80.0% | **100.0% (5/5)** | PASS |
| Average Document Analysis Latency (CPU) | < 30.0s | **0.65s** | PASS |
| Automated Test Suite & Coverage | Pass | **106 / 106 passed (88% coverage)** | PASS |
| External API Calls & Cloud Cost | 0 | **0 calls / ₹0** | PASS |

**Speaker Notes:**  
Clarify honestly that `100%` quote offset match verifies that every quoted excerpt is an exact slice of the extracted text (no altered wording), while clause and risk accuracy are measured separately against annotated gold JSON files.

---

## Slide 10 — Limitations & Future Scope

**Honest Limitations:**
- **Not legal advice:** Informational reference tool only; formal legal decisions require a qualified advocate or court.
- **Rule-based simplification style:** Safely preserves numbers, dates, and negations (`not`, `unless`, `except`), though output prose is more structured and less conversational than human paraphrasing.
- **Language & format bounds:** Currently supports English legal documents; `.docx` page numbers are character-count estimates since Word files do not embed rendered page breaks.

**Future Scope:**
- **Indian Regional Languages:** Translate and simplify into Hindi, Telugu, Tamil, Kannada, and Marathi using local Indic NLP models (`IndicTrans2` / `MuRIL`).
- **Complete Statutory Coverage:** Expand `indian_statutes.yaml` to cover all 358 BNS sections, BNSS criminal procedure sections, and BSA evidence sections.
- **Indian Legal Transformer Fine-Tuning:** Fine-tune `InLegalBERT` on annotated Indian contracts and High Court judgments for higher classification accuracy.

**Speaker Notes:**  
Being transparent about current limits and presenting realistic, concrete next steps demonstrates strong engineering maturity during viva Q&A.

---

## Slide 11 — 5-Minute Live Demo Flow

1. **Legal Issue Helper (`/helper`):** Type *"Someone promised me a job online, took ₹50,000 via UPI, and blocked my number"* -> show matched IT Act Sec. 66C/66D + BNS Sec. 318, Helpline 1930 steps, then enter *"how to bake a cake"* to show honest non-match refusal.
2. **Studio & BNS/IPC Lookup (`/studio`):** Search `420` -> show BNS 318 <-> IPC 420 mapping -> click **Simplify** to demonstrate Simple / Detailed / Professional modes, readability score gain, and matched legal glossary terms.
3. **Full Document Analysis (`/upload` -> `/documents/<id>`):** Upload an Indian contract (`one_sided_agreement.pdf` or `rental_agreement.pdf`) and `bns_selected_sections.pdf` -> show Plain-Language Summary, Detected BNS/IPC References, Clauses, Risk Flags, Key `₹` Facts, Document Q&A (with honest refusal), and 10-section PDF download.

---

## Slide 12 — Likely Viva Questions & Answers

1. **Q: Why use local NLP models instead of calling an external API?**  
   **A:** Legal documents contain sensitive personal and financial details. Running locally guarantees zero data leaves the user's machine, zero API cost, ~0.65s processing speed, and 100% verbatim offset-verified quotes without generative hallucinations.
2. **Q: How do you ensure the app does not give unauthorized legal advice?**  
   **A:** `soften_legal_claims()` filters out definitive conclusions (*"illegal"*, *"void"*, *"unenforceable"*), missing provisions are strictly labeled `"Possible omission"`, and both the UI and PDF reports show a clear informational notice along with the NALSA free legal aid helpline (`15100`).
3. **Q: How does Document Q&A avoid inventing answers when a topic is not in the document?**  
   **A:** Hybrid SBERT + BM25 Reciprocal Rank Fusion retrieves the top chunks, and `deepset/minilm-uncased-squad2` compares the best span logit against its unanswerable null logit. If `best_span_score - null_score < 0.0`, it returns *"The document does not appear to address this."*
4. **Q: How did you adapt the NLP pipeline specifically for India?**  
   **A:** We added Indian 2-digit rupee comma extraction (`₹18,00,000.00`), Carlito TrueType PDF fonts for crisp `₹` rendering, alphanumeric Indian section/article segmentation (`Article 21A`, `Section 498A`), a 200+ term Indian legal glossary, offline BNS 2023 <-> IPC 1860 & Constitution lookup, and the SBERT-powered Indian Legal Issue Helper.
