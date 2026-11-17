# 5-Minute Demo Walkthrough

This guide covers a straightforward 5-minute demonstration of KanoonSaathi running locally at `http://127.0.0.1:5000`.

## Before you start

Make sure the app is running (`./run_local.sh`) and keep `samples/contracts/rental_agreement.pdf` and `samples/contracts/one_sided_agreement.pdf` ready to upload.

## 1. Landing page, sign-in, and dashboard (0:00 - 1:00)

1. Open `http://127.0.0.1:5000` to show the landing page and the honest limits list (not legal advice, extractive summaries, rule-based simplification, runs locally).
2. Sign in (or register a fresh account).
3. On the dashboard, point out:
   - Totals are queried directly from MySQL for the logged-in user (a brand-new account shows zeros and an empty state).
   - Risk charts by category and severity are drawn locally with Chart.js from `app/static/vendor/chart.js`.
   - Light and dark mode toggle cleanly in the top bar.

## 2. Upload and text extraction (1:00 - 2:00)

1. Open **Upload** and choose `samples/contracts/one_sided_agreement.pdf` (or `rental_agreement.pdf`).
2. Mention the upload checks: `.pdf`/`.docx`/`.txt` extensions, magic-byte validation (`%PDF`, `PK\x03\x04`), 10 MB limit, and SHA-256 duplicate detection per user.
3. Wait about a second for extraction and analysis to complete, then open the **Text Chunks** tab to show the extracted page text with page numbers.

## 3. Clauses and simplification (2:00 - 3:00)

1. Open the **Extracted Clauses** tab:
   - Filter by importance (`High`, `Medium`, `Low`), category, or keyword search.
   - Show the `"From the document"` badge and exact character slice quote. Note that the source-match percentage checks that every quote is an exact slice of the extracted text, not an LLM paraphrase.
   - Switch a clause between **Simple English**, **Detailed**, and **Professional** modes.
2. Open **Studio** (`/studio`), load one of the sample clauses, and click **Analyze** to show the before/after Flesch Reading Ease score, matched glossary terms, and trap warnings.

## 4. Key info, risk flags, and Q&A (3:00 - 4:15)

1. Open **Key Information**: show extracted amounts, dates, notice periods, and parties, and point out that absent fields explicitly say `"Not specified"` instead of guessing.
2. Open **Risk Analysis** and **Missing Provisions**:
   - Show severity tags (`High`, `Medium`, `Low`), source quotes, and suggested questions to ask.
   - Note that wording avoids absolute legal conclusions (no "illegal" or "void") and missing checks are labeled `"Possible omission"`.
3. Open **Document Q&A**:
   - Ask a question covered by the contract (for example, `"What is the monthly rent amount and when is it due?"` on `rental_agreement.pdf`) and point out the page citation.
   - Ask an off-topic question (for example, `"What is the employee stock option vesting schedule?"`) to show the honest refusal: `"The document does not appear to address this."`

## 5. PDF report and wrap-up (4:15 - 5:00)

1. Click **Download report** in the document header to open the 10-section ReportLab PDF.
2. Point out the running header/footer (`Page X of Y`), Unicode currency and legal symbols (`$`, `₹`, `§`), provenance labels, and closing disclaimer.
3. Wrap up by noting that the entire demo ran offline with zero external API calls and zero cloud cost, and mention the real trade-offs (rule-based simplification sounds less natural than a large LLM, and the LEDGAR model was trained on US corporate contracts).
