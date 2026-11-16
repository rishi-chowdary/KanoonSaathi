# LexiLegal AI

LexiLegal AI is a system for simplifying legal agreements and highlighting critical clauses, financial terms, obligations, and potential risks. Every extracted finding cites the source page and includes verbatim quote verification against the original document text.

The project is structured into three services:
1. **Frontend**: React 18 single-page application built with Vite and Tailwind CSS.
2. **Backend**: Java 21 / Spring Boot 3 service of record managing authentication, document metadata, storage, full-text retrieval, and PDF reports.
3. **AI Engine**: Python 3.11+ / FastAPI service handling text extraction, OCR, chunking, and structured LLM analysis.

---

## Prerequisites

- **Java**: OpenJDK 21 or higher
- **Maven**: 3.8+
- **Node.js**: 20+ with npm
- **Python**: 3.11+ with venv
- **PostgreSQL**: 16+ (local service or via Docker/Podman)
- **Tesseract OCR**: Optional for scanned document processing (`sudo dnf install tesseract tesseract-langpack-eng` on Fedora)

---

## Environment Setup

Copy the example environment configuration:

```bash
cp .env.example .env
```

Review `.env` to adjust database credentials or configure your Gemini API key:
- Set `GEMINI_API_KEY` to your key if using Gemini.
- Or set `LLM_PROVIDER=ollama` to run against a local Ollama instance (`ollama run llama3`).

---

## Running the Services

### 1. Database

Start PostgreSQL via Docker or Podman Compose:

```bash
docker compose up -d postgres
# or with podman:
podman compose up -d postgres
```

Alternatively, run against an existing local PostgreSQL instance listening on the port configured in `.env` (default: 5433).

### 2. AI Engine (FastAPI)

From the project root:

```bash
cd ai-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify the service is running:

```bash
curl http://localhost:8000/health
```

### 3. Backend (Spring Boot)

From the project root:

```bash
cd backend
mvn spring-boot:run
```

Verify backend and database connectivity:

```bash
curl http://localhost:8080/api/health
```

Verify service-to-service communication between backend and AI engine:

```bash
curl http://localhost:8080/api/health/ai
```

Access Swagger UI interactive API documentation:
`http://localhost:8080/swagger-ui.html`

### 4. Frontend (Vite + React)

From the project root:

```bash
cd frontend
npm install
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## Running Tests

Run backend unit and integration tests:

```bash
cd backend && mvn test
```

Run AI engine tests:

```bash
cd ai-engine && .venv/bin/pytest
```

Run frontend build check:

```bash
cd frontend && npm run build
```

