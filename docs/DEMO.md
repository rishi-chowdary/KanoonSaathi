# LexiLegal AI — 5-Minute Evaluation & Viva Demo Script

This script provides an exact 5-minute step-by-step walkthrough for project examiners and evaluators to demonstrate all key features of the LexiLegal AI local Python NLP platform.

---

## ⏱️ Timeline & Agenda

| Time | Phase | Target Demonstration | Key Takeaway |
|---|---|---|---|
| **0:00 – 1:00** | **System Overview & Dashboard** | Login, Tenant Isolation, Real SQL Stats, Chart.js Visuals | Pure Python stack, zero hardcoded numbers |
| **1:00 – 2:00** | **Document Upload & Ingestion** | Upload `rental_agreement.pdf`, Extraction, Chunk Inspector | Verifiable character offsets, fast sub-second analysis |
| **2:00 – 3:00** | **Clause Inventory & Simplification** | Tri-Tier modes, Flesch Reading Score, Exact Quote Verification | 100% exact substring slice invariant |
| **3:00 – 4:00** | **Risk Detection & Grounded Q&A** | Predatory terms, Rule 7 Guard, SQuAD 2.0 honest refusal | Zero hallucination, strict legal guardrails |
| **4:00 – 5:00** | **ReportLab PDF Dossier & Wrap-up** | 10-section PDF download, Running headers, Offline privacy | 100% on-premise execution, zero cloud APIs |

---

## Step-by-Step Walkthrough

### 1. Overview & Dashboard (0:00 – 1:00)
1. **Open the web application** at `http://127.0.0.1:5000`.
2. **Log in** with evaluator credentials (or click **Register** to create a fresh user in 5 seconds).
3. **Show Dashboard**:
   - Highlight the real-time aggregate metric cards: *Total Contracts*, *Analyzed*, *Identified Clauses*, *Risk Findings*, and *Average Verification Rate (100.0%)*.
   - Point out the **Risk Category Doughnut Chart** and **Risk Severity Bar Chart** rendered dynamically via local static Chart.js (zero external CDN).
   - Demonstrate **Tenant Isolation**: Show that statistics are strictly queried for `current_user.id` using real SQL aggregation; user accounts never leak data across sessions.

### 2. Document Upload & Ingestion (1:00 – 2:00)
1. Click **Upload Document** in the navigation header.
2. Note the file validation safeguards: 10MB size limit, extension filtering (`.pdf`, `.docx`, `.txt`), magic byte verification (`%PDF`, `PK\x03\x04`), and SHA-256 duplicate content detection.
3. Select and upload `samples/contracts/rental_agreement.pdf` (or `one_sided_agreement.pdf`).
4. Review the completed document overview:
   - Extraction executes in **under 0.5 seconds** (over 25x faster than cloud LLM APIs).
   - Inspect the **Raw Text & Pages** tab showing exact layout-preserved page blocks.

### 3. Clause Analysis & Tri-Tier Simplification (2:00 – 3:00)
1. Open the **Clause Analysis** tab:
   - Filter clauses by category (*Payment Terms*, *Termination*, *Governing Law*) and importance (*High*, *Medium*, *Low*).
   - Point out the **"✓ Quote Verified" badge**: 100% of quotes are exact substring slices verified against character offsets in source text.
2. Demonstrate **Tri-Tier Simplification Modes**:
   - *Simple English*: Plain-language explanation for consumer comprehension (5th–8th grade reading level).
   - *Detailed Context*: Balanced contractual explanation for operations teams.
   - *Professional Summary*: Commercial legal perspective with obligor/obligation structure.
3. Open the **Simplification Studio** (`/studio`):
   - Paste any convoluted contract clause.
   - Show the live **Flesch Reading Ease** and **Flesch-Kincaid Grade Level** scores alongside legal glossary term tooltips.

### 4. Grounded Risk Detection & Document Q&A (3:00 – 4:00)
1. Switch to the **Risk Analysis** tab:
   - Show color-coded severity badges (`HIGH`, `MEDIUM`, `LOW`) with evidence quotes and "Why This Matters" explanations.
   - Point out **Rule 7 Compliance**: The system never uses forbidden words like *"illegal"*, *"void"*, or *"unenforceable"*, framing all findings as non-definitive advisory observations.
   - Point out **Rule 6 Compliance**: Absent contract fields strictly display `"Not specified"`.
   - Point out **Missing Provisions**: Standard omitted clauses are clearly tagged `"Possible omission"`.
2. Open the **Document Q&A** tab:
   - Click starter chip: *"What is the monthly rent amount and when is it due?"*
   - Show assistant response citing `✓ Page 1` with exact grounded dollar amount ($2,400.00).
   - **Hallucination & Honesty Probe**: Ask about non-existent terms (e.g., *"What is the tenant's post-employment non-compete restriction?"*).
   - Demonstrate the **Honest Refusal Invariant**: The system truthfully responds *"The document does not appear to address this."* without inventing facts or hallucinating citations.

### 5. ReportLab PDF Dossier & Offline Privacy (4:00 – 5:00)
1. Click **📄 Download PDF Report** in the document header.
2. Open the downloaded PDF dossier:
   - Walk through all **10 structured sections**: Executive Summary, Key Provisions, Tri-Tier Explanations, Grounded Risks, Financial Commitments, Critical Dates, Missing Provisions Checklist, Counsel Questions, and Regulatory Notice with SHA-256 integrity hash.
   - Note the two-pass running header and footer with dynamic page numbers (`Page X of Y`).
   - Note the crisp TrueType Unicode font rendering currency and legal symbols (`$`, `₹`, `§`, bullets).
3. **Viva Conclusion**:
   - Emphasize that **0 external API calls** were made, **0 cloud tokens** were consumed, and **$0.00** was spent on external services.
   - The entire platform runs locally with complete data privacy, deterministic reproducibility, and verifiable factual grounding.
