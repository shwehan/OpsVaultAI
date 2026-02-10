# OpsVaultAI — Interview Talk Track

> Behavioral stories (STAR): `docs/stories.md`

## 30–60 second version
I’m building OpsVaultAI, an API-first inbox/ticket assistant that answers policy and knowledge-base questions with citations. Today it supports `POST /ask`: it retrieves the most relevant KB excerpts from an indexed document set and returns top-k citations with a latency metric. I also built a small evaluation harness to measure recall@k and retrieval latency so I can iterate on chunking/retrieval quality with evidence. Next I’ll add grounded generation, triage/risk scoring, and deploy to AWS (ECR → ECS Fargate) with observability.

## 4–5 minute version (structured)
### Problem
Support and ops teams spend time searching policy docs and replying to repetitive inbound questions. The risk is inconsistent answers, slow response times, and poor escalation handling.

### Users
- Support/ops agents handling inbound tickets
- Risk/fraud teams triaging suspicious or policy-sensitive requests
- Product teams who want measurable improvements (latency, deflection rate)

### Solution (what I built)
- FastAPI backend with `/ask` returning citations from a KB index
- Dependency-free indexing + retrieval pipeline so it’s easy to run and demo
- Evaluation harness measuring recall@k and p50/p95 latency on a golden set

### Architecture (1 minute)
- Docs in `data/kb` → chunked into `data/index.jsonl`
- `/ask` loads index (cached), retrieves top-k chunks, returns citations + latency
- Designed so generation + reranking can plug in later without changing the API

### Metrics & iteration plan
- Today: recall@k and retrieval latency
- Next: groundedness/faithfulness + citation coverage; monitor p50/p95 latency and cost per query in production

### Tradeoffs
- Started with simple retrieval scaffolding to ship quickly and build eval discipline
- Chose citations-first to reduce hallucination risk when LLM generation is added
- API-first to make deployment and integration easier

### Next steps
- Add LLM-based grounded answer generation + guardrails
- Add triage endpoint with structured outputs (category, priority, risk_score)
- Deploy to AWS and add observability (CloudWatch/OTel traces)

