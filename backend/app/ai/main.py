from fastapi import FastAPI
from mangum import Mangum

from app.ai.routers import ai

app = FastAPI(title="Poco AI Orchestrator")

app.include_router(ai.router, prefix="/ai", tags=["ai"])


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "ai"}


# Lambda B entrypoint
handler = Mangum(app)
