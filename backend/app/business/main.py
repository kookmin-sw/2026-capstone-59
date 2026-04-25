from fastapi import FastAPI
from mangum import Mangum

from app.business.routers import projects, stages, steps
from app.core import exception_handlers

app = FastAPI(title="Poco Business API")

exception_handlers.register(app)

app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(stages.router, prefix="/stages", tags=["stages"])
app.include_router(steps.router, prefix="/steps", tags=["steps"])


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "business"}


handler = Mangum(app)
