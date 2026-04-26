from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.ai.routers import steps
from app.core import exception_handlers

app = FastAPI(title="Poco AI Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exception_handlers.register(app)
app.include_router(steps.router, tags=["ai"])


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "ai"}


# Lambda B entrypoint
handler = Mangum(app)
