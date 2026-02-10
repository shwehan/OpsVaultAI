from fastapi import FastAPI
from pydantic import BaseModel
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.rag.retrieve import get_index
from backend.app.triage import triage_message


app = FastAPI(title="OpsVault AI")

class AskRequest(BaseModel):
   question: str = Field(..., min_length=1)
   k: int = Field(5, ge=1, le=10)
    
class Citation(BaseModel):
    source_id: str
    snippet: str
    score: float

class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]
    latency_ms: int

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

    # # Minimal "answer" for Day 1: retrieval-grounded summary placeholder.
    # if citations:
    #     answer = (
    #         "I found relevant policy/KB excerpts. "
    #         "See citations for the most relevant sources."
    #     )
    # else:
    #     answer = "I couldn't find relevant sources in the current index."
    # Minimal grounded answer (extractive): show top excerpts as the answer.
    if citations:
        top = citations[:2]
        lines = [f"- [{c.source_id}] {c.snippet}" for c in top]
        answer = "Most relevant KB excerpts:\n" + "\n".join(lines)
    else:
        answer = "I couldn't find relevant sources in the current index."

    latency_ms = int((time.time() - t0) * 1000)

    return AskResponse(answer=answer, citations=citations, latency_ms=latency_ms)


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
