# OpsVault AI

OpsVault AI is a small “knowledge + action” assistant:
1) Answers questions from internal docs with citations (RAG)
2) Triage inbound messages and drafts grounded replies (agent workflow)

## Who it’s for
Small teams (ops/support/sales) that waste time searching PDFs/FAQs and replying to repetitive emails.

## Features (Roadmap)
- Week 0: API scaffold + sample data
- Week 1: Docker + AWS deploy (ECS Fargate)
- Week 2: RAG with citations + eval harness
- Week 3: LangGraph action agent + safe tools
- Week 4: CI/CD + monitoring + guardrails
- Week 5: Interview-ready polish + case study

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
