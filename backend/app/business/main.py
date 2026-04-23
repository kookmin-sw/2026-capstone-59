from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.business.routers import projects, stages, steps

app = FastAPI(title="Poco Business API")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "error": exc.detail},
    )


app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(stages.router, prefix="/stages", tags=["stages"])
app.include_router(steps.router, prefix="/steps", tags=["steps"])


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "business"}


handler = Mangum(app)