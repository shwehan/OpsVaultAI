cat > docs/demo_script_90s.md << 'EOF'
# OpsVaultAI — 90s Demo Script

**0–10s (Problem)**
Ops teams lose time searching policy docs and replying to repetitive tickets. The risk is slow responses and inconsistent answers.

**10–35s (What I built)**
OpsVaultAI is an API-first assistant. It indexes a KB and exposes `POST /ask` that returns the most relevant excerpts with citations and latency.

**35–70s (Live demo)**
1) Build index:
```bash
python -m backend.app.rag.ingest --docs data/kb --out data/index.jsonl
