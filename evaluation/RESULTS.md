# KanoonSaathi — Evaluation Results

**Date**: November 18, 2026  
**Pipeline**: Local Python NLP (DistilBERT LEDGAR fallback + SBERT `all-MiniLM-L6-v2` + spaCy `en_core_web_md` + `minilm-uncased-squad2`)  
**Backend**: Flask / SQLAlchemy / MySQL 8  
**External API calls**: 0 (runs offline)

## Summary

These benchmarks measure the local Python NLP pipeline against the annotated sample contracts in `samples/gold/` and the 15 questions in `evaluation/chat_questions.json`.

- **Clause quotes**: 100.0% matched in source. Because clause text is sliced directly by character offsets from the extracted text, this checks offset integrity rather than model accuracy.
- **Non-advisory wording**: 0 disallowed legal conclusion terms ("illegal", "void", "unenforceable") across all risk outputs.
- **Missing field defaults**: 0 invented values for fields that should default to `"Not specified"`.
- **One-sided contract traps**: 3/3 detected in `one_sided_agreement.pdf`.
- **Document chat**: 90.0% (9/10) answerable accuracy, 80.0% (8/10) page accuracy, and 100.0% (5/5) refusals on unanswerable questions.
- **Latency**: Average pipeline time is 0.65s per sample contract on CPU (0 external tokens).

## Core Metrics

| Category | Metric | Target | Legacy LLM Baseline | Local Python NLP | Status |
|---|---|---|---:|---:|---|
| Clause Extraction | Recall | >= 80.0% | 100.0% | 100.0% | PASS |
| | Precision | >= 75.0% | 100.0% | 85.7% | PASS |
| | F1 | >= 0.80 | 1.000 | 0.923 | PASS |
| | Source offset match | >= 85.0% | 91.2% | 100.0% | PASS |
| Risk Detection | Recall vs gold | >= 70.0% | 92.3% (12/13) | 100.0% (10/10) | PASS |
| | Precision | >= 70.0% | 100.0% | 100.0% | PASS |
| | F1 | >= 0.70 | 0.960 | 1.000 | PASS |
| | One-sided traps | 3/3 | 3/3 | 3/3 | PASS |
| Wording & Defaults | Disallowed legal claims | 0 | 0 | 0 | PASS |
| | Missing field defaults | 0 invented | 0 invented | 0 invented (100.0% accuracy) | PASS |
| | Missing provision label | "Possible omission" | 100.0% | 100.0% | PASS |
| Document Chat | Answerable accuracy | >= 80.0% | 100.0% (10/10) | 90.0% (9/10) | PASS |
| | Citation page accuracy | >= 80.0% | 100.0% (10/10) | 80.0% (8/10) | PASS |
| | Unanswerable refusal | >= 80.0% | 100.0% (5/5) | 100.0% (5/5) | PASS |
| | Prompt injection test | Ignored | Passed | Passed | PASS |
| Performance | Avg pipeline latency | < 30.0s | 12.4s | 0.65s | PASS |
| | Interactive QA latency | < 5.0s | 1.8s | ~0.12s | PASS |
| | External API tokens | 0 | ~7,480 | 0 | PASS |

## Stage Latency Breakdown

| Pipeline Stage | Legacy LLM Baseline | Local Python NLP | Ratio |
|---|---:|---:|---:|
| Extraction (PyMuPDF / python-docx / OCR) | 0.80s | 0.005s | ~160.0x |
| Clause Segmentation | - | 0.000s | local |
| Clause Classification | 4.20s | 0.125s | ~33.6x |
| Extractive Summarization (TextRank + MMR) | 2.50s | 0.258s | ~9.7x |
| Key Information Extraction | 1.30s | 0.004s | ~325.0x |
| Risk Detection | 2.60s | 0.245s | ~10.6x |
| Missing Provisions Check | 1.00s | 0.009s | ~111.1x |
| **Total Pipeline** | **12.40s** | **0.65s** | **~19.2x** |
| **PDF Report Generation (ReportLab)** | 0.25s | ~0.15s | ~1.7x |
