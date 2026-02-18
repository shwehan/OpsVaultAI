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
