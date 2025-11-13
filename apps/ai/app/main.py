from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Service")

class TrajectoryRequest(BaseModel):
    speeds: list[float] = []
    gaps: list[float] = []

class TrajectoryResponse(BaseModel):
    anomaly_score: float

class NLPRequest(BaseModel):
    text: str
    language: str | None = None

class NLPResponse(BaseModel):
    label: str
    confidence: float

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/anomaly/trajectory-score", response_model=TrajectoryResponse)
async def trajectory_score(req: TrajectoryRequest):
    # Dummy scoring: std of speeds + avg gap as proxy
    import numpy as np
    score = float(np.std(req.speeds or [0.0]) + np.mean(req.gaps or [0.0]))
    return {"anomaly_score": min(score, 1.0)}

@app.post("/nlp/classify", response_model=NLPResponse)
async def nlp_classify(req: NLPRequest):
    text = (req.text or "").lower()
    if any(k in text for k in ["help", "sos", "panic", "attack", "harass", "hospital", "lost"]):
        return {"label": "emergency", "confidence": 0.85}
    return {"label": "other", "confidence": 0.6}
