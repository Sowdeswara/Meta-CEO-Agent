from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import uvicorn
import threading

from helm.main import HELM
from helm.config import Config

app = FastAPI(title="HELM v2.0 API")

# Serve frontend static files from ./frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Global helm instance (initialized on startup)
helm_instance: Optional[HELM] = None
helm_lock = threading.Lock()


class DecisionRequest(BaseModel):
    prompt: str = Field(..., description="User prompt for the decision")
    context: Dict[str, Any] = Field(default_factory=dict)
    required_fields: List[str] = Field(default_factory=list)


class DecisionResponse(BaseModel):
    decision: str  # Decision status as string
    confidence: float
    roi: float
    scores: Dict[str, float]
    arbitration_score: float
    validation_score: float
    reasoning: Dict[str, Any]
    decision_id: str
    agent_used: str
    decision_text: str
    risk_level: str
    status: str
    timestamp: Optional[str]


@app.on_event("startup")
def startup_event():
    global helm_instance
    cfg = Config()
    # Ensure demo + development mode so we can skip system checks in local runs
    cfg.DEMO_MODE = True
    cfg.DEVELOPMENT_MODE = True

    # Initialize HELM with skip_system_check True per migration requirements
    helm_instance = HELM(enable_local_model=False, enable_dashboard=False, skip_system_check=True, config=cfg)


@app.on_event("shutdown")
def shutdown_event():
    global helm_instance
    if helm_instance:
        try:
            helm_instance.shutdown()
        except Exception:
            pass


@app.get("/", response_class=HTMLResponse)
def root():
    # Serve the frontend index as the root
    index_path = "frontend/index.html"
    try:
        return FileResponse(index_path)
    except Exception:
        return HTMLResponse(content="<h3>HELM v2.0 API</h3><p>Visit <a href=\"/static/index.html\">UI</a></p>", status_code=200)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/decision", response_model=DecisionResponse)
def run_decision(req: DecisionRequest):
    global helm_instance
    if not helm_instance:
        raise HTTPException(status_code=503, detail="HELM not initialized")

    # HELM is deterministic and synchronous; protect with a lock
    with helm_lock:
        try:
            decision = helm_instance.process_decision(req.prompt, req.context or {}, req.required_fields or [])
            return DecisionResponse(**decision)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
def history(limit: int = 20):
    global helm_instance
    if not helm_instance:
        raise HTTPException(status_code=503, detail="HELM not initialized")
    try:
        data = helm_instance.get_decision_history(limit)
        return {"history": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
