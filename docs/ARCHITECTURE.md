# OpsVaultAI Architecture

## What it is
OpsVaultAI is an API-first inbox/ticket assistant that answers questions using a policy/KB knowledge base (RAG) and returns citations for transparency.

## Current scope (Day 1 MVP)
- FastAPI service exposes:
  - `GET /health`
  - `POST /ask` (retrieval + citations)
  - `POST /triage` (stub / next milestone)
- Retrieval uses a simple chunk index built from `data/kb/` and returns top-k sources + snippets.

## Data flow: /ask
1. User sends a question to `POST /ask`
2. Service loads `data/index.jsonl` (cached by file mtime)
3. Computes query representation and similarity vs indexed chunks
4. Returns:
   - a lightweight answer placeholder (generation can be added later)
   - citations: `{source_id, snippet, score}`
   - `latency_ms`

## Indexing
- `python -m backend.app.rag.ingest --docs data/kb --out data/index.jsonl`
- Docs are chunked (chars-based) with overlap to preserve context.
- Each chunk stores:
  - `source_id` (relative path)
  - `chunk_id`
  - `text`
  - `vector` (dependency-free hashed TF vector)

## Key tradeoffs (today)
- **Dependency-free retrieval** vs embedding-based vectors:
  - Pro: simple, fast to run locally, good for scaffolding + evaluation harness
  - Con: weaker semantic matching than real embeddings; will be upgraded later
- **Citations-first**:
  - Pro: supports trust and mitigates hallucinations in later generation step
  - Con: requires careful chunking and prompt/answer constraints when LLM is added
- **API-first**:
  - Pro: easy to deploy + integrate with any UI/tools
  - Con: demo UX is less polished without a UI

## Planned next steps
- Replace hashed TF vectors with embeddings + vector DB (FAISS/pgvector) and optional reranking
- Add grounded generation (LLM) that must cite sources for each claim
- Add eval beyond retrieval: faithfulness / citation coverage
- Add AWS deployment: ECR -> ECS Fargate + ALB + CloudWatch/OTel