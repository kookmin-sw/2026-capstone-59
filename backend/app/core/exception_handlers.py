from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import PocoError


def register(app: FastAPI) -> None:
    @app.exception_handler(PocoError)
    async def poco_error_handler(request: Request, exc: PocoError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error": {"code": exc.code, "message": exc.message},
            },
        )
