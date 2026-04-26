from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.business.routers import auth, projects, stages, steps
from app.core import exception_handlers

app = FastAPI(title="Poco Business API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exception_handlers.register(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(stages.router, prefix="/stages", tags=["stages"])
app.include_router(steps.router, prefix="/steps", tags=["steps"])


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "business"}


handler = Mangum(app)
