# Migration Notes

LexiLegal AI was first prototyped as a multi-service stack before being consolidated into the current single Python application. This note records what changed and why, so historical references in git history make sense.

## Earlier prototype (archived before tag `v2.0-nlp-migrated`)

The original prototype split the project across three servers and an external LLM:

- **Frontend**: React 18, Vite, Tailwind CSS, Recharts
- **Backend**: Spring Boot 3 (Java 21), Spring Security JWT auth, Flyway migrations, OpenPDF
- **AI Engine**: FastAPI calling the Google Gemini API (`gemini-2.5-flash-lite`)
- **Database**: PostgreSQL 16 with `ts_rank` full-text search

## Why it was replaced

1. **Privacy and cost**: Sending full contract text to a hosted API conflicted with local-only document review and depended on external API quotas and availability.
2. **Traceability**: Generative summaries and risk paragraphs could paraphrase or drop qualifying words (`unless`, `except`, `subject to`). Using extractive slicing and deterministic rules keeps every quote tied to exact character offsets.
3. **Simpler local setup**: Running Node, Java/Maven, Python/FastAPI, and PostgreSQL together was fragile on a student laptop. Moving to one Flask process and MySQL 8 reduced startup to `./run_local.sh`.

## Current stack mapping

| Area | Earlier prototype | Current implementation |
|---|---|---|
| Web UI | React 18 + Tailwind + Recharts | Jinja2 templates + hand-written CSS + vanilla JS + local Chart.js |
| Server & Auth | Spring Boot 3 + stateless JWT | Flask 3 + Flask-Login sessions (`HttpOnly`, `SameSite=Lax`) + CSRF |
| Database | PostgreSQL 16 + Flyway | MySQL 8 (`InnoDB`, `utf8mb4`) + Flask-Migrate (Alembic) |
| Clause extraction | Gemini JSON prompts | Heading/sentence segmentation + LEDGAR DistilBERT + SBERT + keyword rules |
| Summaries | Gemini map-reduce | Extractive SBERT TextRank + Maximal Marginal Relevance (MMR) |
| Simplification | Gemini rewrites | Rule-based glossary (151 terms) + sentence splitting + templates + Flesch scores |
| Risk & omissions | Gemini prompts | YAML risk rules (`data/risk_rules.yaml`) + SBERT prototypes + expected checklists |
| Document chat | PostgreSQL FTS + Gemini | Hybrid SBERT + BM25 (RRF) + fact intent router + `minilm-uncased-squad2` QA |
| PDF report | Java OpenPDF | Python ReportLab with local TrueType fonts |

Baseline measurements from the earlier Gemini prototype are archived in `evaluation/baseline_llm/` for side-by-side comparison in `evaluation/RESULTS.md`.
