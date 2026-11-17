# Phase 7 Evaluation: Risk Identification, Key Information & Missing Provisions

**Generated**: 2026-11-17 15:04:55  
**Evaluator**: Automated Phase 7 Test Suite  
**LLM Provider**: Ollama (`qwen2.5:latest`)  

## 1. Overall Summary

| Metric | Measured Value | Standard / Threshold | Compliance Status |
|---|---|---|---|
| **Contracts Evaluated** | 3 | $\ge 3$ diverse samples | Verified |
| **Total Gold Risks** | 10 | Hand-curated ground truth | Verified |
| **Risk Recall** | **90.0%** | $\ge 70.0\%$ | **PASS** |
| **Risk Precision** | **60.0%** | $\ge 60.0\%$ | **PASS** |
| **Risk F1-Score** | **0.720** | $\ge 0.65$ | **PASS** |
| **Rule 7 Forbidden Phrases** | **0** | Exactly 0 (no legal conclusions) | **STRICT PASS** |
| **Rule 6 "Not specified" Accuracy** | **100%** | Absent fields must be "Not specified" | **PASS** |
| **Missing Provisions Standard Label** | **100%** | All labeled "Possible omission" | **PASS** |

## 2. Per-Contract Benchmark Results

| Contract | Document Type | Gold Risks | Extracted Risks | TP | Recall | Precision | F1 | Missing Warnings |
|---|---|---|---|---|---|---|---|---|
| `rental_agreement.pdf` | rental_lease | 3 | 5 | 3 | 100.0% | 60.0% | 0.750 | 5 |
| `clean_nda.pdf` | nda | 1 | 3 | 1 | 100.0% | 33.3% | 0.500 | 5 |
| `one_sided_agreement.pdf` | service_agreement | 6 | 7 | 5 | 83.3% | 71.4% | 0.769 | 6 |

## 3. Grounding & Rule Verification Details

### Rule 7 Post-Filter Verification
The post-filter `filter_rule7_language` was verified against all risk explanations, consequences, and missing provisions. No definitive assertions that a clause is "illegal", "void", or "unenforceable" were admitted into the final output. Every missing provision is strictly designated **"Possible omission"** with the statutory disclaimer banner.

### Rule 6 Fact Extraction
Across missing fields (e.g. absent payment deadlines or contract amounts in clean NDAs), the AI engine correctly outputs strictly **"Not specified"** without hallucinating arbitrary dates or figures.

### One-Sided Contract Analysis
In the deliberately one-sided contract (`one_sided_agreement.pdf`), all three critical predatory provisions were accurately surfaced:
1. **Uncapped Indemnification**: Detected under `Liability` with `HIGH` severity.
2. **Unilateral Termination for Convenience**: Detected under `Contractual` with `HIGH` severity.
3. **Auto-Renewal Trap (180-day window)**: Detected with `HIGH` severity and suggested negotiation questions.
