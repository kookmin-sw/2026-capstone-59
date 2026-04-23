from fastapi import FastAPI, Request
from fastapi import status as http_status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AIServiceUnavailableError,
    BadRequestError,
    InternalError,
    InvalidStateError,
    NotFoundError,
    NotionServiceUnavailableError,
    PocoError,
    StageCompletionBlockedError,
    ValidationError,
)


def _error_response(status_code: int, exc: PocoError, extra: dict | None = None) -> JSONResponse:
    error = {"code": exc.code, "message": exc.message}
    if extra:
        error.update(extra)
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "error": error},
    )


def register(app: FastAPI) -> None:
    @app.exception_handler(BadRequestError)
    async def bad_request_handler(request: Request, exc: BadRequestError):
        return _error_response(http_status.HTTP_400_BAD_REQUEST, exc)

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return _error_response(http_status.HTTP_404_NOT_FOUND, exc)

    @app.exception_handler(InvalidStateError)
    async def invalid_state_handler(request: Request, exc: InvalidStateError):
        return _error_response(http_status.HTTP_409_CONFLICT, exc)

    @app.exception_handler(StageCompletionBlockedError)
    async def stage_completion_blocked_handler(request: Request, exc: StageCompletionBlockedError):
        return _error_response(
            http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            exc,
            extra={"details": exc.details} if exc.details else None,
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return _error_response(http_status.HTTP_422_UNPROCESSABLE_ENTITY, exc)

    @app.exception_handler(InternalError)
    async def internal_error_handler(request: Request, exc: InternalError):
        return _error_response(http_status.HTTP_500_INTERNAL_SERVER_ERROR, exc)

    @app.exception_handler(AIServiceUnavailableError)
    async def ai_service_unavailable_handler(request: Request, exc: AIServiceUnavailableError):
        return _error_response(http_status.HTTP_503_SERVICE_UNAVAILABLE, exc)

    @app.exception_handler(NotionServiceUnavailableError)
    async def notion_service_unavailable_handler(request: Request, exc: NotionServiceUnavailableError):
        return _error_response(http_status.HTTP_503_SERVICE_UNAVAILABLE, exc)

    @app.exception_handler(PocoError)
    async def poco_error_handler(request: Request, exc: PocoError):
        return _error_response(http_status.HTTP_500_INTERNAL_SERVER_ERROR, exc)
