"""CSRF Double Submit Cookie 검증 의존성.

원리:
- 로그인 시 csrf_token 을 쿠키(NON-HttpOnly)와 함께 발급
- 프론트엔드는 mutating 요청 시 쿠키에서 csrf_token 을 읽어 X-CSRF-Token 헤더에 첨부
- 다른 사이트는 우리 도메인 쿠키를 JS로 읽지 못하므로 헤더 위조 불가 → CSRF 차단

예외 — Bearer 헤더 인증:
- AI Lambda Function URL 처럼 별도 도메인 호출은 쿠키가 안 가므로
  Authorization: Bearer <token> 으로 인증한다.
- 이 경우 브라우저가 자동 첨부하는 자격증명이 없어 CSRF 공격 자체가 성립 불가
  (공격자가 sessionStorage 의 access_token 을 못 훔치는 한).
- 따라서 Bearer 인증 요청은 CSRF 검증을 생략한다.
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
    authorization: str | None = Header(default=None),
) -> None:
    """state-changing 메서드(POST/PUT/PATCH/DELETE)에서만 검증.
    GET/HEAD/OPTIONS는 부수효과가 없으므로 검증 생략.

    Bearer 헤더로 인증한 요청은 CSRF 공격 불가능하므로 검증 생략.
    """
    if request.method not in _MUTATING_METHODS:
        return
    if authorization and authorization.lower().startswith("bearer "):
        return
    if not csrf_cookie or not csrf_header:
        raise InvalidTokenError("CSRF 토큰이 누락되었습니다.")
    if not secrets.compare_digest(csrf_cookie, csrf_header):
        raise InvalidTokenError("CSRF 토큰이 일치하지 않습니다.")
