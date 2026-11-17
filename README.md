# LexiLegal AI — Legal Contract Simplification & Analysis Platform

LexiLegal AI is an enterprise-grade legal document analysis and simplification platform. It transforms complex legal agreements (leases, NDAs, employment agreements, vendor contracts) into plain-language summaries, structured clause inventories, grounded risk assessments, and verifiable citations.

Every extracted finding cites the source page and includes verbatim quote verification against original document text.

The system is organized into three services:
1. **Frontend**: React 18 single-page application built with Vite, Tailwind CSS, Lucide icons, and Recharts analytics.
2. **Backend**: Java 21 / Spring Boot 3 service of record managing authentication, tenant-isolated document storage, PostgreSQL full-text search RAG, and 10-section OpenPDF dossier generation.
3. **AI Engine**: Python 3.11+ / FastAPI service handling PyMuPDF layout-aware extraction, OCR, sliding-window chunking, quote verification, and structured LLM analysis (Gemini or Mock).

---

## 🚀 Quick Start (One Command)

To launch all three services with a single command:

```bash
chmod +x run_local.sh
./run_local.sh
```

This starts:
- **FastAPI AI Engine**: `http://localhost:8000`
- **Spring Boot Backend**: `http://localhost:8080/api` (Swagger UI at `/swagger-ui.html`)
- **React Frontend**: `http://localhost:5173`

Press `Ctrl+C` at any time to shut down all background services gracefully.

---

## 📋 Prerequisites

- **Java**: OpenJDK 21 or higher
- **Maven**: 3.8+
- **Node.js**: 20+ with npm
- **Python**: 3.11+ with `venv`
- **PostgreSQL**: 16+ (local or Supabase pooler)
- **Tesseract OCR**: Optional for scanned document OCR (`sudo dnf install tesseract tesseract-langpack-eng` or `apt install tesseract-ocr`)

---

## ⚙️ Environment Configuration

Copy the example environment configuration:

```bash
cp .env.example .env
```

Key environment variables:
| Variable | Description | Default |
|---|---|---|
| `SPRING_DATASOURCE_URL` | PostgreSQL JDBC connection URL | `jdbc:postgresql://localhost:5433/lexilegal` |
| `SPRING_DATASOURCE_USERNAME` | Database username | `postgres` |
| `SPRING_DATASOURCE_PASSWORD` | Database password | `postgres` |
| `JWT_SECRET` | 256-bit secret key for HMAC-SHA256 | Configured in `.env` |
| `JWT_EXPIRATION_HOURS` | Token lifetime | `24` |
| `AI_ENGINE_URL` | URL to FastAPI microservice | `http://localhost:8000` |
| `INTERNAL_API_KEY` | Shared secret header between services | Configured in `.env` |
| `GEMINI_API_KEY` | Google Gemini API key | Optional (uses mock if absent) |
| `USE_MOCK_LLM` | Enable offline deterministic mock LLM | `false` |
| `MAX_FILE_SIZE_MB` | File upload ceiling | `10` |

---

## 🧪 Testing Suite

### 1. End-to-End Smoke Test
Run the full automated end-to-end smoke test script:
```bash
./scripts/smoke_test.sh
```
*Covers: Health check $\rightarrow$ User registration $\rightarrow$ Contract upload $\rightarrow$ Async pipeline polling $\rightarrow$ Clause extraction verification $\rightarrow$ RAG chat query $\rightarrow$ 10-section PDF report generation.*

### 2. Backend Tests (Spring Boot)
```bash
cd backend && mvn test
```
*Executes 32 unit and integration tests across controllers, security, rate limiters, PDF generation, and tenant isolation.*

### 3. AI Engine Tests (Pytest)
```bash
cd ai-engine && .venv/bin/pytest
```
*Executes 57 tests covering extraction, OCR, chunking, quote verification, Rule 7 forbidden phrase filters, and offline recorded-fixture suites.*

### 4. Frontend Component Tests (Vitest + RTL)
```bash
cd frontend && npm test
```
*Executes Vitest and React Testing Library tests for authentication, upload file validation (10MB, empty, format checks), and clause filters.*

### 5. Benchmark & Evaluation Suite
```bash
python3 evaluation/verify_phase9.py
python3 evaluation/evaluate_phase7.py
python3 evaluation/evaluate_chat.py
```
*Full evaluation results and accuracy tables are documented in [evaluation/RESULTS.md](file:///home/rishichowdary/Documents/lexilegal-ai/evaluation/RESULTS.md).*

---

## 📚 Documentation Links

- **[docs/architecture.md](file:///home/rishichowdary/Documents/lexilegal-ai/docs/architecture.md)**: System architecture and Mermaid diagrams (Async Pipeline, RAG Search).
- **[docs/api-documentation.md](file:///home/rishichowdary/Documents/lexilegal-ai/docs/api-documentation.md)**: Comprehensive REST API reference and schema definitions.
- **[docs/privacy.md](file:///home/rishichowdary/Documents/lexilegal-ai/docs/privacy.md)**: Data privacy architecture, zero-training LLM boundary, and cascade deletion.
- **[docs/DEMO.md](file:///home/rishichowdary/Documents/lexilegal-ai/docs/DEMO.md)**: 5-minute evaluator demonstration and viva walkthrough script.
- **[evaluation/RESULTS.md](file:///home/rishichowdary/Documents/lexilegal-ai/evaluation/RESULTS.md)**: Full precision, recall, hallucination probe, and latency metrics.
- **[Postman Collection](file:///home/rishichowdary/Documents/lexilegal-ai/postman/lexilegal.postman_collection.json)**: Ready-to-import Postman workspace.

---

## 🔧 Troubleshooting

### 1. Database Connection Issues
If connecting to Supabase:
- Ensure the connection URL uses transaction pooler mode (`aws-0-...pooler.supabase.com:6543/postgres`).
- Verify IPv4 pooler mode if the local environment lacks IPv6 egress.

### 2. PDF Font Rendering
If special currency symbols (`₹`) or legal section signs (`§`) render as `?` in generated PDF reports:
- Ensure system TrueType fonts are available (`/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf` or `fonts-noto-core`).
- `ReportPdfService` will automatically fall back to standard Helvetica if custom TTF files are missing.

### 3. AI Engine Timeout Handling
- The backend incorporates an automatic retry mechanism with exponential backoff for transient 5xx or connection drops.
- When the backend restarts, any documents stranded in `ANALYZING` state are automatically marked `FAILED` with a recovery message so users can click *Re-analyze*.
