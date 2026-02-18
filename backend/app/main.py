from fastapi import FastAPI
from pydantic import BaseModel
import time
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.app.rag.retrieve import get_index
from backend.app.triage import triage_message

from backend.app.observability import request_id_and_timing_middleware

app = FastAPI(title="OpsVault AI")

STOPWORDS = {
    "what", "is", "the", "a", "an", "your", "our", "do", "does", "we", "are",
    "to", "of", "and", "or", "in", "on", "for", "with", "how"
}
GENERIC = {"policy", "process", "help", "support"}

def extract_keywords(q: str) -> list[str]:
    tokens = [t.strip(".,?!:;()[]{}\"'").lower() for t in (q or "").split()]
    tokens = [t for t in tokens if len(t) >= 4 and t not in STOPWORDS and t not in GENERIC]
    return tokens

app.middleware("http")(request_id_and_timing_middleware)


# class AskRequest(BaseModel):
#    question: str = Field(..., min_length=1)
#    k: int = Field(5, ge=1, le=10)

class AskRequest(BaseModel):
    question: str
    k: int = 3
    min_score: float = 0.12  # guardrail threshold
 
class Citation(BaseModel):
    source_id: str
    snippet: str
    score: float

# class AskResponse(BaseModel):
#     answer: str
#     citations: List[Citation]
#     latency_ms: int
class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    latency_ms: int
    abstained: bool = False
    abstain_reason: Optional[str] = None

@app.get("/")
def root():
    return {
        "name": "OpsVault AI",
        "status": "running",
        "endpoints": ["/health", "/docs", "/ask", "/triage"]
    }

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

    # Keyword-missing guardrail (prevents generic matches like "policy" from passing)
    keywords = extract_keywords(req.question)
    joined = " ".join([c.snippet.lower() for c in citations])
    missing = [kw for kw in keywords if kw not in joined]
    missing_keywords = (len(keywords) > 0 and len(missing) == len(keywords))

    abstained = low_score or missing_keywords
    abstain_reason = None

    if abstained:
        if low_score:
            abstain_reason = (
                f"low_retrieval_confidence: top_score={top_score:.3f} < min_score={req.min_score:.3f}"
            )
        else:
            abstain_reason = f"missing_query_keywords: {missing}"

        answer = "I couldn't find relevant sources in the current knowledge base. Try rephrasing or add more docs."
    else:
        top = citations[:2]
        lines = [f"- [{c.source_id}] {c.snippet}" for c in top]
        answer = "Most relevant KB excerpts:\n" + "\n".join(lines)

    latency_ms = int((time.time() - t0) * 1000)

    return AskResponse(
        answer=answer,
        citations=citations,
        latency_ms=latency_ms,
        abstained=abstained,
        abstain_reason=abstain_reason,
    )


# @app.post("/triage")
# def triage(payload: dict):
#     # Week 0: stub
#     return {
#         "label": "support",
#         "confidence": 0.5,
#         "draft_reply": "Stub reply (Week 0).",
#         "used_sources": []
#     }

class TriageRequest(BaseModel):
    message: str 


class TriageResponse(BaseModel):
    category: str 
    priority: str 
    risk_score: float
    rationale: list[str]
    next_action: str 
    suggested_reply: str 

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
