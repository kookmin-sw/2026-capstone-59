"""공통 응답 envelope.

라우터는 EnvelopeRouter(app/core/api/route.py)를 사용하면
반환값이 자동으로 SuccessResponse(data=...) 로 래핑된다.
이 스키마는 EnvelopeRoute의 자동 래핑과 OpenAPI 스키마 생성에 사용된다.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: T | None = None
