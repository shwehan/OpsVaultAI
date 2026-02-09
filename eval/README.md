# OpsVaultAI — Retrieval Evaluation

This folder contains a small, reproducible evaluation harness for the retrieval step of RAG.

## What we measure (today)
- **Recall@k**: whether at least one expected source appears in the top-k retrieved results
- **Latency**: retrieval time (p50/p95)

## Run
From repo root:

```bash
python eval/run_eval.py