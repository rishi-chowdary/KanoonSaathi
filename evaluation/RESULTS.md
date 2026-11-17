# LexiLegal AI — Evaluation Benchmark Results

**Evaluation Suite Version**: 2.0.0 (Python NLP Migration)  
**Date**: November 18, 2026  
**Inference Engine**: Local Python NLP Pipeline (DistilBERT LEDGAR + SBERT `all-MiniLM-L6-v2` + spaCy `en_core_web_md` + `minilm-uncased-squad2`)  
**Backend & Database**: Flask 3.1 / SQLAlchemy / MySQL 8 (InnoDB, utf8mb4)  
**API Call Dependencies**: **0 External API Calls** (100% Offline, Zero Cloud Tokens, Zero API Cost)

---

## 1. Executive Summary & Parity Verification

Following the architectural migration from the legacy distributed stack (React + Spring Boot + FastAPI + Gemini 3.5 Flash Lite) to the pure local Python NLP stack, LexiLegal AI underwent rigorous offline benchmark evaluation across 6 contract categories (Standard Lease, Non-Disclosure Agreement, Executive Employment, One-Sided Master Services Agreement, Commercial Loan, Promissory Note).

### Key Architectural Gains:
1. **Verifiable Fact Grounding**: Clause quote verification rate achieved **100.0%** (vs 91.2% in LLM stack) by enforcing exact substring character slice offsets directly against extracted source text.
2. **Deterministic Regulatory Guardrails**:
   - **Rule 7 Compliance**: **0 violations** across all generated outputs (100% elimination of unauthorized conclusions like "illegal", "void", "unenforceable").
   - **Rule 6 Compliance**: **0 violations** (100% strict adherence to defaulting absent attributes to `"Not specified"`).
3. **Predatory Contract Traps**: Successfully surfaced **3/3 critical predatory traps** in `one_sided_agreement.pdf` (uncapped indemnity, unilateral termination rights with fee acceleration, and 180-day automatic renewal traps).
4. **Document Chat Honesty**:
   - Answer accuracy on answerable contract queries: **100.0%** (10/10).
   - Page citation accuracy: **90.0%** (9/10).
   - Honest refusal rate on unanswerable questions: **100.0%** (5/5) via SQuAD 2.0 unanswerable thresholding.
5. **Speed, Privacy & Cost**:
   - Average document analysis pipeline latency reduced from **12.4s -> 0.56s** (**>22.1x speedup**).
   - Cloud tokens per contract reduced from **~7,480 tokens -> 0 tokens**.
   - Cloud cost per contract reduced from **~$0.00042 -> $0.00000** with **100% local data privacy**.

---

## 2. Core Metrics Summary: Old Stack vs. New NLP Stack

| Category | Benchmark Metric | Target Standard | Old Stack (Gemini API) | New Stack (Local Python NLP) | Status |
|---|---|---|---|---|---|
| **Clause Extraction** | Clause Recall | $\ge 80.0\%$ | 100.0% | **100.0%** | **PASS** |
| | Clause Precision | $\ge 75.0\%$ | 100.0% | **85.7%** | **PASS** |
| | Clause F1-Score | $\ge 0.80$ | 1.000 | **0.923** | **PASS** |
| | Quote Verification Rate | $\ge 85.0\%$ | 91.2% | **100.0%** | **EXCEEDS** |
| **Risk Detection** | Risk Recall vs. Gold | $\ge 70.0\%$ | 92.3% (12/13) | **100.0%** (10/10) | **PASS** |
| | Risk Precision | $\ge 70.0\%$ | 100.0% | **90.9%** | **PASS** |
| | Risk F1-Score | $\ge 0.70$ | 0.960 | **0.952** | **PASS** |
| | Predatory Clause Detection | 100% on one-sided | 3/3 Detected | **3/3 Detected** | **PASS** |
| **Regulatory Guardrails** | Rule 7 Forbidden Phrase Count | Exactly 0 | 0 | **0** | **STRICT PASS** |
| | Rule 6 "Not specified" Accuracy | 100% | 100.0% | **100.0%** (0 violations) | **PASS** |
| | Missing Provision Disclaimer | 100% labeled "Possible omission" | 100.0% | **100.0%** | **PASS** |
| **RAG Document Chat** | Answer Correctness Rate | $\ge 80.0\%$ | 100.0% (10/10) | **100.0%** (10/10) | **PASS** |
| | Citation Page Accuracy | $\ge 80.0\%$ | 100.0% (10/10) | **90.0%** (9/10) | **PASS** |
| | Honest Refusal ("Not Found") Rate | $\ge 80.0\%$ | 100.0% (5/5) | **100.0%** (5/5) | **PASS** |
| | Prompt Injection Resistance | Ignore instructions | Passed | **Passed (100% resistant)** | **PASS** |
| **Performance & Cost** | Average Pipeline Latency | $< 30.0\text{s}$ | 12.4s | **0.56s** | **PASS** |
| | Interactive QA Latency | $< 5.0\text{s}$ | 1.8s | **~0.12s** | **PASS** |
| | Average Tokens / Document | Budget $\le 10,000$ | ~7,480 tokens | **0 tokens** | **OPTIMAL** |
| | Average Cloud Cost / Doc | Budget $\le \$0.01$ | ~$0.00042 | **$0.00 (Zero)** | **OPTIMAL** |
| | Cloud Network Dependency | Offline capable | Requires internet | **100% Offline** | **PASS** |

---

## 3. Detailed Component Breakdown

### 3.1 Clause Extraction & Classification Ensemble
- **Architecture**:
  1. DistilBERT fine-tuned on LEDGAR legal provisions dataset.
  2. Dense semantic similarity against 17 category prototypes in `data/clause_prototypes.yaml` using SBERT `all-MiniLM-L6-v2`.
  3. High-precision legal keyword and title regex rules.
- **Quote Verification Invariant**:
  Unlike LLM generation which frequently hallucinated words or omitted trailing syllables (yielding 91.2% verification in Phase 10), the local NLP extractor anchors quotes directly to exact character offsets (`original_text[start:end]`), ensuring a verifiable **100.0% Quote Verification Rate**.

### 3.2 Grounded Risk Engine & Predatory Contract Probes
In `one_sided_agreement.pdf` (specifically crafted to test edge-case predatory traps):
1. **Uncapped & Unilateral Indemnity**: Flagged as `HIGH` risk under `Liability`. Customer indemnifies Vendor without limitation including legal fees.
2. **Unilateral Termination for Convenience**: Flagged as `HIGH` risk under `Contractual`. Only Vendor may terminate without cause, while Customer termination triggers acceleration of all future fees.
3. **Automatic Renewal Trap**: Flagged as `MEDIUM` risk under `Contractual` with strict 180-day certified mail notice window.
4. **Disproportionate Liability Cap**: Flagged as `HIGH` risk under `Liability`. Vendor caps aggregate liability at nominal $100.00 while Customer bears uncapped liability.
5. **Severe Late Interest**: Flagged as `HIGH` risk under `Financial`. 2.5% monthly late interest compounded daily alongside $500 administrative fee.
6. **Unilateral Fee Modification**: Flagged as `HIGH` risk under `Contractual`. Vendor may unilaterally revise fees at any time without consent.

### 3.3 Rule 7 Legal Conclusion Safeguards
A deterministic post-processor sanitizes any conclusionary legal assertions (*"illegal"*, *"void"*, *"unenforceable"*, *"unlawful"*). Outputs consistently use calibrated non-definitive advisory phrasing (*"presents substantial exposure"*, *"may be unfavorable under standard commercial practices"*, *"questionable under statutory review"*).
- Measured violations: **0**.

### 3.4 Hybrid Passage Retrieval & Extractive QA
- **Hybrid Retrieval**: Dense SBERT cosine ranking + Sparse BM25 lexical ranking combined via Reciprocal Rank Fusion ($k=60$).
- **Fact Intent Routing**: Queries on signatories, amounts, dates, deadlines, penalties, and governing law are answered directly from verified metadata with 100% precision and exact page citations.
- **Honest Refusal Invariant**: Questions regarding provisions absent from the document (e.g. non-compete terms in an apartment lease, or dental insurance in an MSA) trigger honest refusal (*"The document does not appear to address this."*) with `addressedInDocument=False` and zero hallucinated citations.

---

## 4. Latency & Resource Utilization Comparison

| Pipeline Stage | Legacy Stack (Gemini API) | Migrated Stack (Local Python NLP) | Speedup Factor |
|---|---|---|---|
| Document Ingestion & PyMuPDF Extraction | 0.80s | 0.004s | ~200.0x |
| Legal Clause Segmentation | — | 0.000s | Local In-Memory |
| Clause Ensemble Classification | 4.20s | 0.181s | ~23.2x |
| Extractive Summarization (TextRank + MMR) | 2.50s | 0.153s | ~16.3x |
| Key Facts & Entity Anchoring | 1.30s | 0.002s | ~650.0x |
| Grounded Risk & Consequence Detection | 2.60s | 0.212s | ~12.3x |
| Expected Provisions Checklist Matching | 1.00s | 0.008s | ~125.0x |
| **Full End-to-End Analysis Pipeline** | **12.40s** | **0.56s** | **~22.1x Faster** |
| **Interactive Document Chat Turn** | **1.80s** | **~0.12s** | **~15.0x Faster** |
| **ReportLab 10-Section PDF Dossier Generation** | 0.25s | ~0.15s | ~1.7x Faster |
