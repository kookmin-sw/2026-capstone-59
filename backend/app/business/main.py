from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.business.routers import auth, projects, stages, steps
from app.core import exception_handlers
from app.core.auth.csrf import verify_csrf
from app.core.auth.dependencies import get_current_user
from app.core.config import settings
from app.core.schemas.health import HealthResponse

app = FastAPI(title="Poco Business API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exception_handlers.register(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])

_protected = [Depends(get_current_user), Depends(verify_csrf)]
app.include_router(
    projects.router, prefix="/projects", tags=["projects"], dependencies=_protected
)
app.include_router(
    stages.router, prefix="/stages", tags=["stages"], dependencies=_protected
)
app.include_router(
    steps.router, prefix="/steps", tags=["steps"], dependencies=_protected
)


@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse(ok=True, service="business")


handler = Mangum(app)
