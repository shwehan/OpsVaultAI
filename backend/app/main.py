from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="OpsVault AI")

class AskRequest(BaseModel):
    question: str
    
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

@app.post("/ask")
def ask(req: AskRequest):
    # Week 0: stub
    return {
        "answer": "Stub answer (Week 0).",
        "citations": []
    }

@app.post("/triage")
def triage(payload: dict):
    # Week 0: stub
    return {
        "label": "support",
        "confidence": 0.5,
        "draft_reply": "Stub reply (Week 0).",
        "used_sources": []
    }
