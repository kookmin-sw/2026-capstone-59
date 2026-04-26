from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.business.routers import auth, projects, stages, steps
from app.core import exception_handlers
from app.core.auth.dependencies import get_current_user

app = FastAPI(title="Poco Business API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exception_handlers.register(app)

# /auth 는 인증 없이 공개
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# 나머지 라우터는 유효한 Bearer Access Token 필수
_auth = [Depends(get_current_user)]
app.include_router(projects.router, prefix="/projects", tags=["projects"], dependencies=_auth)
app.include_router(stages.router, prefix="/stages", tags=["stages"], dependencies=_auth)
app.include_router(steps.router, prefix="/steps", tags=["steps"], dependencies=_auth)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "business"}


handler = Mangum(app)
