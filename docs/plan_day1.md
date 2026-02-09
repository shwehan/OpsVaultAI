# Day 1 Plan — RAG MVP + Eval Harness 

## Day 1 Repo Milestone (must ship)
**Ask endpoint does real retrieval + returns citations; eval script runs; tests + docs included.**

### Acceptance criteria
- [ ] `POST /ask` returns: `{ answer, citations:[{source_id, snippet, score}], latency_ms }`
- [ ] `python eval/run_eval.py` prints recall@k + latency summary
- [ ] `pytest` passes (health + ask contract + retrieval smoke)
- [ ] README includes: Run (docker), Build index (if applicable), Demo curl, Architecture diagram

---

## Blocks + exact outputs

### Block A — Setup (20m)
- [ ] Create branch `day1-rag-eval`
- [ ] Add this plan doc
- [ ] Add `docs/demo_steps.md` (placeholder)
- [ ] Commit

### Block B — Local/Docker smoke test (30–45m)
- [ ] Run API (local or docker)
- [ ] Verify `/health` and `/docs`
- [ ] Add README “How to run” (docker + local)
- [ ] Commit

### Block C — Ingest + index build (80m)
- [ ] Add `rag/ingest` module + CLI command
- [ ] Chunk docs + store metadata: source_id/title/chunk_id
- [ ] Document command in README
- [ ] Commit

### Block D — Retrieval + `/ask` returns citations (80m)
- [ ] Add `rag/retrieve` module with `retrieve(query, k)`
- [ ] Update `/ask` to call retrieve and return citations
- [ ] LLM optional; fallback to retrieval-only ok
- [ ] Commit

### Block E — Tests (60m)
- [ ] Add `pytest` tests: `/health` + `/ask` contract + retrieval smoke
- [ ] Commit

### Block F — Eval harness (60m)
- [ ] `eval/golden_questions.jsonl` with expected_sources
- [ ] `eval/run_eval.py` prints recall@k and latency
- [ ] `eval/README.md` explains metrics + next steps
- [ ] Commit

### Block G — Docs for interviews (50m)
- [ ] `docs/ARCHITECTURE.md` (flow + tradeoffs)
- [ ] `docs/TALK_TRACK.md` (problem→build→metrics→next)
- [ ] `docs/interview_rag_eval.md` (1-page cheat sheet)
- [ ] Commit

