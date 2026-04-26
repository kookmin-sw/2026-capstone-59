from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.ai.routers import steps
from app.core import exception_handlers
from app.core.auth.dependencies import get_current_user_id

app = FastAPI(title="Poco AI Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exception_handlers.register(app)

# 모든 AI 라우터는 유효한 Bearer Access Token 필수 (DB 조회 없이 토큰만 검증)
app.include_router(steps.router, tags=["ai"], dependencies=[Depends(get_current_user_id)])


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "ai"}


# Lambda B entrypoint
handler = Mangum(app)
