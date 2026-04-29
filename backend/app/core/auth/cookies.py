"""인증 쿠키 set/clear 헬퍼.

쿠키 3종 구성:
- access_token : HttpOnly, Path=/             (모든 요청에 자동 첨부)
- refresh_token: HttpOnly, Path=/auth         (refresh/logout에서만 노출)
- csrf_token   : NOT HttpOnly, Path=/         (JS가 읽어 X-CSRF-Token 헤더에 실음)
"""

import secrets

from fastapi import Response

from app.core.config import settings


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    csrf_token: str,
) -> None:
    common = {
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "domain": settings.COOKIE_DOMAIN,
    }

    response.set_cookie(
        settings.ACCESS_COOKIE_NAME,
        access_token,
        httponly=True,
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **common,
    )
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        refresh_token,
        httponly=True,
        path="/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        **common,
    )
    response.set_cookie(
        settings.CSRF_COOKIE_NAME,
        csrf_token,
        httponly=False,
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **common,
    )


def clear_auth_cookies(response: Response) -> None:
    for name, path in (
        (settings.ACCESS_COOKIE_NAME, "/"),
        (settings.REFRESH_COOKIE_NAME, "/auth"),
        (settings.CSRF_COOKIE_NAME, "/"),
    ):
        response.delete_cookie(name, path=path, domain=settings.COOKIE_DOMAIN)
