# RAG + Evaluation — Interview Cheat Sheet (OpsVaultAI)

## RAG basics I can explain
- **Chunking**: size/overlap tradeoff; too small loses context, too big hurts retrieval specificity
- **Retrieval**: top-k selection; optional reranking; filtering by doc type/recency
- **Grounding**: citations; "no citation, no claim"; abstain when context is missing

## What can go wrong (and how I'd mitigate)
- Wrong chunk retrieved → improve chunking, add reranker, better embeddings
- Hallucinations → citations + constrained prompting + refusal when no evidence
- Prompt injection in docs → treat docs as untrusted, strip instructions, sandbox tools
- Stale policies → doc versioning, recency weighting, human review flow

## Metrics I’d use
### Retrieval quality
- **Recall@k**, MRR, nDCG (if you have graded relevance)
- Coverage: how often expected sources appear in top-k

### System performance
- Latency p50/p95 (retrieval + generation), throughput, error rate
- Cost per request (token usage) once LLM is added

### Answer quality (after LLM generation)
- Faithfulness / groundedness (claims supported by citations)
- Citation coverage: % of sentences/claims backed by sources

## How I’d run experiments (Product DS angle)
- Define success metrics: deflection rate, resolution time, CSAT, escalations
- A/B test with guardrails (latency, wrong-answer rate)
- Iterate based on eval + real-world feedback loops

## Fraud/Risk angle (how this extends)
- Triage output can include category, priority, risk_score, rationale
- Evaluate with PR-AUC, calibration, cost-sensitive thresholds, drift monitoring
