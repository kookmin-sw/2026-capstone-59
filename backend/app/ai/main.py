from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.ai.routers import steps, projects
from app.core import exception_handlers
from app.core.auth.csrf import verify_csrf
from app.core.auth.dependencies import get_current_user_id
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.schemas.health import HealthResponse

setup_logging()

app = FastAPI(title="Poco AI Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exception_handlers.register(app)

_protected = [Depends(get_current_user_id), Depends(verify_csrf)]
app.include_router(
    steps.router, prefix="/steps", tags=["ai"], dependencies=_protected
)
app.include_router(
    projects.router, prefix="/projects", tags=["ai"], dependencies=_protected
)


@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse(ok=True, service="ai")


# Lambda B entrypoint
handler = Mangum(app)
