from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.ai.routers import steps
from app.core import exception_handlers
from app.core.auth.csrf import verify_csrf
from app.core.auth.dependencies import get_current_user_id
from app.core.config import settings
from app.core.schemas.health import HealthResponse

app = FastAPI(title="Poco AI Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exception_handlers.register(app)

app.include_router(
    steps.router,
    tags=["ai"],
    dependencies=[Depends(get_current_user_id), Depends(verify_csrf)],
)


@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse(ok=True, service="ai")


# Lambda B entrypoint
handler = Mangum(app)
