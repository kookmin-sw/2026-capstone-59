"""CSRF Double Submit Cookie 검증 의존성.

원리:
- 로그인 시 csrf_token을 쿠키(NON-HttpOnly)와 함께 발급
- 프론트엔드는 mutating 요청 시 쿠키에서 csrf_token을 읽어 X-CSRF-Token 헤더에 첨부
- 다른 사이트는 우리 도메인 쿠키를 JS로 읽지 못하므로 헤더 위조 불가 → CSRF 차단
"""

import secrets

from fastapi import Cookie, Header, Request

from app.core.config import settings
from app.core.exceptions import InvalidTokenError

_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def verify_csrf(
    request: Request,
    csrf_cookie: str | None = Cookie(default=None, alias=settings.CSRF_COOKIE_NAME),
    csrf_header: str | None = Header(default=None, alias=settings.CSRF_HEADER_NAME),
) -> None:
    """state-changing 메서드(POST/PUT/PATCH/DELETE)에서만 검증.
    GET/HEAD/OPTIONS는 부수효과가 없으므로 검증 생략."""
    if request.method not in _MUTATING_METHODS:
        return
    if not csrf_cookie or not csrf_header:
        raise InvalidTokenError("CSRF 토큰이 누락되었습니다.")
    if not secrets.compare_digest(csrf_cookie, csrf_header):
        raise InvalidTokenError("CSRF 토큰이 일치하지 않습니다.")
