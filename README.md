# OpsVault AI

OpsVault AI is a small “knowledge + action” assistant:
1) Answers questions from internal docs with citations (RAG)
2) Triage inbound messages and drafts grounded replies (agent workflow)

## Who it’s for
Small teams (ops/support/sales) that waste time searching PDFs/FAQs and replying to repetitive emails.

## Features (Roadmap)
- 0: API scaffold + sample data
- 1: Docker + AWS deploy (ECS Fargate)
- 2: RAG with citations + eval harness
- 3: LangGraph action agent + safe tools
- 4: CI/CD + monitoring + guardrails

## Architecture
```mermaid
flowchart LR
  U[Inbox / User] --> API[FastAPI API]
  API --> RAG[RAG Engine]
  RAG --> VDB[(Vector Store)]
  RAG --> DOCS[(Docs Storage)]
  API --> LOGS[Logs/Tracing]

## Run the API (local)

```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000


Now update `docs/demo_steps.md` with the **exact working commands** (no placeholders). For example:

```md
# Demo Steps (Day 1)

## Run (Docker)
```bash
docker build -t opsvault-backend -f backend/Dockerfile backend
docker run --rm -p 8000:8000 opsvault-backend

---

### 2D) Commit
```bash
git add README.md docs/demo_steps.md
git commit -m "docs: add local+docker run instructions and demo steps"


## Build the doc index (for retrieval)

```bash
python -m backend.app.rag.ingest --docs <PATH_TO_DOCS_DIR> --out data/index.jsonl


---

## 3G) Commit Step 3
```bash
git add backend/app/rag README.md
git commit -m "feat: ingestion CLI builds JSONL chunk index (dependency-free)"
