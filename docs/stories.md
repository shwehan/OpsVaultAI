# Interview Stories (STAR) — OpsVaultAI + Job Hunt

Use these as flexible modules. Start with the Soundbite (10–20s), then expand to STAR (60–120s).
Tailor the same story to the role by emphasizing metrics (Product DS), risk/cost tradeoffs (Fraud DS), or deployment/ops/customer impact (Solutions/AI Eng).

---

## Story 1 — Shipping fast with quality (Portfolio → Interview-ready proof)

**Soundbite**
I shipped an end-to-end RAG retrieval MVP (index → retrieve → `/ask` citations) with tests and a tiny eval harness, so I can iterate with measurable progress instead of “vibes.”

**S — Situation**
I had a portfolio repo started (FastAPI + Docker + stubs) but it didn’t yet demonstrate the core value or an interview-ready narrative.

**T — Task**
Make it demoable in under 2 minutes and defensible in interviews: clear architecture, measurable retrieval quality, and basic engineering hygiene.

**A — Action**
- Implemented document chunking + indexing into a JSONL index.
- Added deterministic retrieval and `/ask` endpoint returning citations + latency.
- Built a golden-set eval script measuring Recall@k and p50/p95 latency.
- Added pytest contract tests and a reproducible retrieval smoke test.
- Wrote architecture + talk track docs to explain tradeoffs and roadmap.

**R — Result**
- A reviewer can run one command to index docs and one command to query `/ask`.
- I can quote early metrics (Recall@k and latency) and show how I’d improve them (reranking/embeddings/guardrails).
- Repo reads like “real work” (tests, docs, eval), not a toy demo.

**Role angle**
- Product DS: focus on “measurable iteration loop.”
- Fraud DS: focus on “system reliability and monitoring plan.”
- Solutions/AI Eng: focus on “demoability + clean interfaces.”

---

## Story 2 — Designing eval before scaling (Experiment mindset)

**Soundbite**
I didn’t want to add more features without feedback loops, so I built a lightweight eval harness early—recall@k + latency—so improvements are measurable.

**S**
RAG systems can look impressive but regress quietly with small changes (chunking, k, doc updates).

**T**
Create a minimum viable evaluation setup that’s easy to run and expand.

**A**
- Created a small golden question set tied to known KB sources.
- Implemented Recall@k scoring (expected source in top-k) and latency tracking (p50/p95).
- Documented next metrics: faithfulness/groundedness and citation coverage.

**R**
- I can quickly test retrieval changes and prevent regressions.
- I have a credible story for “how I’d run experiments” in production: offline eval → shadow mode → A/B.

**Role angle**
- Product DS: A/B testing, guardrails, decision making.
- AI Eng: quality gates and regression testing.

---

## Story 3 — Handling ambiguity and scoping ruthlessly (Deliver something real)

**Soundbite**
I avoided boiling the ocean: shipped retrieval + citations first, and explicitly scoped LLM generation as a later plug-in once evaluation and interfaces were stable.

**S**
It’s easy to jump straight to agents/LLMs and end up with a brittle demo.

**T**
Pick the smallest set of things that prove value and build a base for future features.

**A**
- API-first design with stable response contracts (`answer`, `citations`, `latency_ms`).
- Retrieval-first “grounded excerpts” answer so the tool is useful even without an LLM.
- Clear roadmap: embeddings + reranker + grounded generation + triage.

**R**
- Faster iteration and clearer debugging.
- Easier to explain in interviews: “Here’s what works now, here’s the next increment.”

**Role angle**
- Solutions: scoping + communicating tradeoffs.
- DS: focusing on measurable impact.

---

## Story 4 — Risk/abuse framing for triage (Fraud/Risk DS + GenAI banking roles)

**Soundbite**
For the triage endpoint, I treat it like a risk system: structured outputs, cost-sensitive thresholds, and monitoring for drift/adaptation.

**S**
Inbound requests can include account takeover attempts, refund abuse, or policy-sensitive issues that need escalation.

**T**
Design a triage schema that supports risk decisions and human-in-the-loop escalation.

**A**
- Defined structured triage output: category, priority, risk_score, rationale, next_action.
- Planned a rules-first baseline with an LLM optional path behind a flag.
- Evaluation approach: PR-AUC/precision-recall focus, calibration checks, cost-based thresholding.
- Monitoring approach: alert on volume shifts, top categories, and false positive rates.

**R**
- A path from “demo triage” to “real risk system” with measurable thresholds and controls.
- Strong narrative for banking GenAI roles: safety, auditability, escalation.

**Role angle**
- Fraud DS: class imbalance, costs, drift.
- Solutions: explain controls clearly to stakeholders.

---

## Story 5 — Observability as a product feature (AI Eng / Solutions)

**Soundbite**
I treat observability as part of the product: request IDs, latency logging, and a plan for traces/alerts so you can trust and operate the system.

**S**
AI systems fail in messy ways (slow retrieval, missing docs, hallucinations). Without observability, you can’t improve them.

**T**
Add lightweight observability early so it’s debuggable and production-ready.

**A**
- Added request_id + consistent latency logging.
- Documented what to add next: OTel traces, dashboards, error budgets, and alerting.
- Defined user-facing reliability: when to abstain, when to escalate, how to surface citations.

**R**
- Clear “operational maturity” signals in the repo and in my story.
- Better interview answers for “how would you run this in prod?”

---

## Story 6 — Customer-first problem solving (Customer Engineer / Solutions Consultant)

**Soundbite**
When I approach a customer problem, I anchor on their workflow and success metrics, then prototype an integration path that’s easy to adopt and prove.

**S**
Many AI products fail because they’re impressive but don’t fit the customer’s actual process.

**T**
Define the smallest pilot that proves value quickly, with low integration friction.

**A**
- Framed a 48-hour pilot: ingest their KB/policies + a sample inbox dataset, deliver a demo API with citations.
- Defined success metrics: deflection rate, time-to-resolution, escalation accuracy, CSAT guardrails.
- Mapped integration: start as internal tool → embed into ticketing system → enforce audit logging and permissions.

**R**
- Clear path from prototype to adoption.
- Strong story for “I can drive a customer from vague ask to measurable pilot.”

---

# Rapid-fire Q&A bullets (use when tired)

## Biggest technical tradeoff you made
- Started with retrieval scaffolding + eval rather than full LLM generation so the system is measurable and debuggable.

## How do you prevent hallucinations?
- Citations-first response contract; “no citation, no claim”; abstain when retrieval confidence is low.

## How would you improve retrieval quality?
- Embeddings + vector DB, reranking, better chunking, metadata filters, and regression tests via golden sets.

## What would you monitor in production?
- Latency p50/p95, error rate, retrieval confidence, citation coverage, and downstream outcomes (deflection, escalations).

## How would you A/B test it?
- Offline eval → shadow mode → A/B with guardrails; define success metrics and roll back conditions.
