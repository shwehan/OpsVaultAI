import os
import time
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.app.llm import generate_answer
from backend.app.observability import request_id_and_timing_middleware
from backend.app.rag.retrieve import get_index
from backend.app.triage import triage_message

load_dotenv()

app = FastAPI(title="OpsVault AI")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OpsVault AI</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0b1120;
      color: #e8eaf0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 48px 16px 80px;
    }

    header { text-align: center; margin-bottom: 36px; }
    header h1 { font-size: 1.9rem; font-weight: 700; color: #fff; letter-spacing: -0.5px; }
    header p  { margin-top: 7px; font-size: 0.95rem; color: #8b94b0; }

    .container { width: 100%; max-width: 740px; }

    /* Tabs */
    .tabs { display: flex; gap: 4px; margin-bottom: 0; }
    .tab-btn {
      flex: 1; padding: 11px; background: #131c30; border: 1px solid #1e2d4a;
      border-bottom: none; border-radius: 8px 8px 0 0; color: #8b94b0;
      font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: color 0.15s, background 0.15s;
    }
    .tab-btn.active { background: #182035; color: #fff; border-color: #2a3f66; }

    /* Card */
    .card {
      background: #131c30; border: 1px solid #1e2d4a; border-radius: 0 0 12px 12px;
      padding: 28px; display: none;
    }
    .card.active { display: block; }

    label { display: block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.07em; color: #8b94b0; margin-bottom: 9px; }

    input[type="text"], textarea {
      width: 100%; padding: 13px 15px; background: #0b1120; border: 1px solid #1e2d4a;
      border-radius: 8px; color: #e8eaf0; font-size: 0.97rem; font-family: inherit;
      outline: none; transition: border-color 0.2s;
    }
    input[type="text"] { height: 48px; }
    textarea { min-height: 110px; resize: vertical; }
    input[type="text"]:focus, textarea:focus { border-color: #3b6aff; }

    button.submit {
      margin-top: 14px; width: 100%; padding: 13px; background: #3b6aff;
      color: #fff; font-size: 0.97rem; font-weight: 600; border: none;
      border-radius: 8px; cursor: pointer; transition: background 0.2s;
    }
    button.submit:hover:not(:disabled) { background: #2d55d6; }
    button.submit:disabled { background: #1e2d4a; color: #8b94b0; cursor: not-allowed; }

    .spinner {
      display: none; margin: 28px auto 0; width: 32px; height: 32px;
      border: 3px solid #1e2d4a; border-top-color: #3b6aff;
      border-radius: 50%; animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    .error-box {
      display: none; margin-top: 20px; padding: 13px 15px;
      background: #2a0f0f; border: 1px solid #7f1d1d;
      border-radius: 8px; color: #fca5a5; font-size: 0.88rem;
    }

    /* Results */
    .results { display: none; margin-top: 28px; }
    .results-title {
      font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.07em; color: #3b6aff; margin-bottom: 14px;
      padding-bottom: 10px; border-bottom: 1px solid #1e2d4a;
    }

    .answer-text {
      font-size: 0.97rem; color: #d0d5e8; line-height: 1.7;
      white-space: pre-wrap; margin-bottom: 18px;
    }

    .meta-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }
    .badge {
      padding: 4px 11px; border-radius: 99px; font-size: 0.78rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.05em;
    }
    .badge-high     { background: #052e16; color: #4ade80; border: 1px solid #166534; }
    .badge-medium   { background: #1c1a07; color: #facc15; border: 1px solid #713f12; }
    .badge-abstain  { background: #1a0a0a; color: #f87171; border: 1px solid #7f1d1d; }
    .badge-p0       { background: #2a0f0f; color: #fca5a5; border: 1px solid #7f1d1d; }
    .badge-p1       { background: #1c1207; color: #fdba74; border: 1px solid #92400e; }
    .badge-p2       { background: #1c1a07; color: #facc15; border: 1px solid #713f12; }
    .badge-p3       { background: #052e16; color: #4ade80; border: 1px solid #166534; }
    .score-label    { font-size: 0.82rem; color: #8b94b0; align-self: center; }

    .section-label {
      font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.07em; color: #3b6aff; margin: 16px 0 7px;
    }
    .field-value { font-size: 0.95rem; color: #d0d5e8; line-height: 1.6; }

    .citations-list { list-style: none; margin-top: 4px; }
    .citations-list li {
      padding: 10px 12px; background: #0d1526; border: 1px solid #1e2d4a;
      border-radius: 6px; margin-bottom: 8px; font-size: 0.88rem; color: #a0aabe; line-height: 1.5;
    }
    .citations-list li strong { color: #6b8aff; font-size: 0.78rem; display: block; margin-bottom: 4px; }

    .rationale-list { padding-left: 0; list-style: none; }
    .rationale-list li {
      padding: 5px 0 5px 14px; position: relative; color: #a0aabe; font-size: 0.9rem;
    }
    .rationale-list li::before { content: "–"; position: absolute; left: 0; color: #3b6aff; }

    .reply-box {
      background: #0d1526; border: 1px solid #1e2d4a; border-radius: 8px;
      padding: 14px 16px; font-size: 0.93rem; color: #d0d5e8; line-height: 1.65;
      font-style: italic; white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <header>
    <h1>OpsVault AI</h1>
    <p>Knowledge base Q&amp;A and inbox triage assistant</p>
  </header>

  <div class="container">
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('ask')">Ask</button>
      <button class="tab-btn" onclick="switchTab('triage')">Triage</button>
    </div>

    <!-- ASK TAB -->
    <div class="card active" id="tab-ask">
      <label for="ask-input">Business Question</label>
      <input type="text" id="ask-input"
             placeholder="e.g. What is the return window for electronics?" />
      <button class="submit" id="ask-btn" onclick="submitAsk()">Ask</button>
      <div class="spinner" id="ask-spinner"></div>
      <div class="error-box" id="ask-error"></div>

      <div class="results" id="ask-results">
        <div class="results-title">Answer</div>
        <div class="answer-text" id="ask-answer"></div>
        <div class="meta-row">
          <span class="badge" id="ask-confidence-badge"></span>
          <span class="score-label" id="ask-score-label"></span>
        </div>
        <div class="section-label" id="ask-citations-header" style="display:none">Sources</div>
        <ul class="citations-list" id="ask-citations"></ul>
      </div>
    </div>

    <!-- TRIAGE TAB -->
    <div class="card" id="tab-triage">
      <label for="triage-input">Inbound Message</label>
      <textarea id="triage-input"
                placeholder="Paste a customer email, support ticket, or message..."></textarea>
      <button class="submit" id="triage-btn" onclick="submitTriage()">Triage</button>
      <div class="spinner" id="triage-spinner"></div>
      <div class="error-box" id="triage-error"></div>

      <div class="results" id="triage-results">
        <div class="results-title">Triage Result</div>
        <div class="meta-row">
          <span class="badge" id="triage-priority-badge"></span>
          <span class="badge" id="triage-category-badge"
                style="background:#0d1526;border:1px solid #2a3f66;color:#6b8aff"></span>
          <span class="score-label" id="triage-score-label"></span>
        </div>
        <div class="section-label">Next Action</div>
        <div class="field-value" id="triage-next-action"></div>
        <div class="section-label">Risk Signals</div>
        <ul class="rationale-list" id="triage-rationale"></ul>
        <div class="section-label">Suggested Reply</div>
        <div class="reply-box" id="triage-reply"></div>
      </div>
    </div>
  </div>

  <script>
    function switchTab(name) {
      document.querySelectorAll(".tab-btn").forEach((b, i) =>
        b.classList.toggle("active", (i === 0) === (name === "ask"))
      );
      document.getElementById("tab-ask").classList.toggle("active", name === "ask");
      document.getElementById("tab-triage").classList.toggle("active", name === "triage");
    }

    function setLoading(prefix, loading) {
      document.getElementById(prefix + "-btn").disabled = loading;
      document.getElementById(prefix + "-btn").textContent = loading ? "Loading…" : (prefix === "ask" ? "Ask" : "Triage");
      document.getElementById(prefix + "-spinner").style.display = loading ? "block" : "none";
      document.getElementById(prefix + "-error").style.display = "none";
    }

    function showError(prefix, msg) {
      const el = document.getElementById(prefix + "-error");
      el.textContent = "Error: " + msg;
      el.style.display = "block";
      document.getElementById(prefix + "-results").style.display = "none";
    }

    async function submitAsk() {
      const question = document.getElementById("ask-input").value.trim();
      if (!question) return;
      setLoading("ask", true);

      try {
        const res = await fetch("/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question })
        });
        if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "Request failed"); }
        const d = await res.json();

        document.getElementById("ask-answer").textContent = d.answer;

        const conf = d.confidence;
        const badge = document.getElementById("ask-confidence-badge");
        badge.textContent = conf.toUpperCase();
        badge.className = "badge badge-" + conf;

        document.getElementById("ask-score-label").textContent =
          "retrieval score: " + (d.retrieval_score ?? 0).toFixed(3);

        const citList = document.getElementById("ask-citations");
        citList.innerHTML = "";
        const header = document.getElementById("ask-citations-header");
        if (d.citations && d.citations.length && !d.abstained) {
          header.style.display = "block";
          d.citations.forEach(c => {
            const li = document.createElement("li");
            li.innerHTML = "<strong>" + c.source_id + " &nbsp;·&nbsp; score: " + c.score.toFixed(3) + "</strong>" + c.snippet;
            citList.appendChild(li);
          });
        } else {
          header.style.display = "none";
        }

        document.getElementById("ask-results").style.display = "block";
      } catch (err) {
        showError("ask", err.message);
      } finally {
        setLoading("ask", false);
      }
    }

    async function submitTriage() {
      const message = document.getElementById("triage-input").value.trim();
      if (!message) return;
      setLoading("triage", true);

      try {
        const res = await fetch("/triage", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message })
        });
        if (!res.ok) { const e = await res.json(); throw new Error(e.detail || "Request failed"); }
        const d = await res.json();

        const pri = d.priority.toLowerCase();
        const pb = document.getElementById("triage-priority-badge");
        pb.textContent = d.priority;
        pb.className = "badge badge-" + pri;

        const cb = document.getElementById("triage-category-badge");
        cb.textContent = d.category.replace(/_/g, " ");

        document.getElementById("triage-score-label").textContent =
          "risk score: " + d.risk_score.toFixed(2);

        document.getElementById("triage-next-action").textContent = d.next_action;

        const ratList = document.getElementById("triage-rationale");
        ratList.innerHTML = "";
        d.rationale.forEach(r => {
          const li = document.createElement("li");
          li.textContent = r;
          ratList.appendChild(li);
        });

        document.getElementById("triage-reply").textContent = d.suggested_reply;
        document.getElementById("triage-results").style.display = "block";
      } catch (err) {
        showError("triage", err.message);
      } finally {
        setLoading("triage", false);
      }
    }

    document.getElementById("ask-input").addEventListener("keydown", e => {
      if (e.key === "Enter") submitAsk();
    });
  </script>
</body>
</html>
"""

STOPWORDS = {
    "what", "is", "the", "a", "an", "your", "our", "do", "does", "we", "are",
    "to", "of", "and", "or", "in", "on", "for", "with", "how"
}
GENERIC = {"policy", "process", "help", "support"}


def extract_keywords(q: str) -> list[str]:
    tokens = [t.strip(".,?!:;()[]{}\"'").lower() for t in (q or "").split()]
    return [t for t in tokens if len(t) >= 4 and t not in STOPWORDS and t not in GENERIC]


app.middleware("http")(request_id_and_timing_middleware)


# ── Models ────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str
    k: int = 3
    min_score: float = 0.12


class Citation(BaseModel):
    source_id: str
    snippet: str
    score: float


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: str            # "high" | "medium" | "abstain"
    retrieval_score: float
    latency_ms: int
    abstained: bool = False
    abstain_reason: Optional[str] = None


class TriageRequest(BaseModel):
    message: str


class TriageResponse(BaseModel):
    category: str
    priority: str
    risk_score: float
    rationale: list[str]
    next_action: str
    suggested_reply: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def root():
    return HTML


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    t0 = time.time()

    index = get_index("data/index.jsonl")
    results = index.retrieve(req.question, k=req.k)

    citations = [
        Citation(source_id=r.source_id, snippet=r.snippet, score=r.score)
        for r in results
        if r.source_id
    ]

    top_score = citations[0].score if citations else 0.0
    low_score = (not citations) or (top_score < req.min_score)

    keywords = extract_keywords(req.question)
    joined = " ".join(c.snippet.lower() for c in citations)
    missing = [kw for kw in keywords if kw not in joined]
    missing_keywords = len(keywords) > 0 and len(missing) == len(keywords)

    abstained = low_score or missing_keywords
    abstain_reason = None

    if abstained:
        abstain_reason = (
            f"low_retrieval_confidence: top_score={top_score:.3f} < min_score={req.min_score:.3f}"
            if low_score
            else f"missing_query_keywords: {missing}"
        )
        answer = (
            "I couldn't find relevant sources in the current knowledge base. "
            "Try rephrasing or add more docs."
        )
        confidence = "abstain"
    else:
        confidence = "high" if top_score >= 0.50 else "medium"
        chunks = [{"source_id": c.source_id, "snippet": c.snippet} for c in citations]
        try:
            answer = generate_answer(req.question, chunks)
        except Exception as exc:
            # Graceful fallback: return excerpts if Groq is unavailable
            answer = "KB excerpts (LLM unavailable):\n" + "\n".join(
                f"[{c.source_id}] {c.snippet}" for c in citations[:2]
            )
            confidence = "medium"

    latency_ms = int((time.time() - t0) * 1000)

    return AskResponse(
        answer=answer,
        citations=citations,
        confidence=confidence,
        retrieval_score=round(top_score, 4),
        latency_ms=latency_ms,
        abstained=abstained,
        abstain_reason=abstain_reason,
    )


@app.post("/triage", response_model=TriageResponse)
def triage(req: TriageRequest):
    d = triage_message(req.message)
    return TriageResponse(
        category=d.category,
        priority=d.priority,
        risk_score=d.risk_score,
        rationale=d.rationale,
        next_action=d.next_action,
        suggested_reply=d.suggested_reply,
    )
