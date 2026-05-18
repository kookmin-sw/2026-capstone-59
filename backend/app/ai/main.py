from fastapi import Depends, FastAPI
from mangum import Mangum

from app.ai.routers import steps, projects
from app.core import exception_handlers
from app.core.auth.csrf import verify_csrf
from app.core.auth.dependencies import get_current_user_id
from app.core.logging import setup_logging
from app.core.schemas.health import HealthResponse

setup_logging()

app = FastAPI(title="Poco AI Orchestrator")

# CORS 는 Function URL 의 CORS 설정으로 edge 에서 처리.
# FastAPI CORSMiddleware 를 켜면 헤더가 중복되어 브라우저가 거부함.

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
