from fastapi import FastAPI
from mangum import Mangum

from app.ai.routers import ai
from app.core import exception_handlers

app = FastAPI(title="Poco AI Orchestrator")

exception_handlers.register(app)
app.include_router(ai.router, tags=["ai"])


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "ai"}


# Lambda B entrypoint
handler = Mangum(app)
