"""공통 응답 envelope 자동 래핑.

EnvelopeRouter를 사용하는 라우터의 모든 엔드포인트는
반환값이 자동으로 SuccessResponse(data=...) 로 래핑된다.
"""

import functools
import inspect
from typing import Any, Callable

from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute, APIRouter
from starlette.responses import Response as StarletteResponse

from app.core.schemas.response import SuccessResponse


def _is_response_class(annotation: Any) -> bool:
    """RedirectResponse, FileResponse 등 Response 서브클래스인지 확인."""
    try:
        return inspect.isclass(annotation) and issubclass(annotation, StarletteResponse)
    except TypeError:
        return False


def _wrap_endpoint(endpoint: Callable) -> Callable:
    """엔드포인트의 반환값을 SuccessResponse로 래핑하여 JSONResponse로 반환."""
    is_async = inspect.iscoroutinefunction(endpoint)

    if is_async:

        @functools.wraps(endpoint)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await endpoint(*args, **kwargs)
            if isinstance(result, StarletteResponse):
                return result
            body = SuccessResponse(data=result).model_dump(mode="json")
            return JSONResponse(content=body)

    else:

        @functools.wraps(endpoint)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = endpoint(*args, **kwargs)
            if isinstance(result, StarletteResponse):
                return result
            body = SuccessResponse(data=result).model_dump(mode="json")
            return JSONResponse(content=body)

    return wrapper


class EnvelopeRoute(APIRoute):
    """엔드포인트를 _wrap_endpoint로 감싸 등록하는 APIRoute."""

    def __init__(self, path: str, endpoint: Callable, **kwargs: Any) -> None:
        # response_model 검증 비활성화 — SuccessResponse 래핑이 이미 타입 안전성을 보장
        kwargs.pop("response_model", None)
        super().__init__(path, _wrap_endpoint(endpoint), response_model=None, **kwargs)


class EnvelopeRouter(APIRouter):
    """기본적으로 EnvelopeRoute를 사용하는 APIRouter."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("route_class", EnvelopeRoute)
        super().__init__(*args, **kwargs)
