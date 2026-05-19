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
    """auth 쿠키 3종 삭제.

    delete_cookie 기본값 (SameSite=Lax, Secure=False) 으로 호출하면
    원본 쿠키 (SameSite=None; Secure) 와 속성 불일치로 cross-site 환경의
    브라우저가 삭제 시도를 무시한다. 원본과 동일한 속성으로 max-age=0 발급.
    """
    common = {
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "domain": settings.COOKIE_DOMAIN,
    }
    for name, path, httponly in (
        (settings.ACCESS_COOKIE_NAME, "/", True),
        (settings.REFRESH_COOKIE_NAME, "/auth", True),
        (settings.CSRF_COOKIE_NAME, "/", False),
    ):
        response.delete_cookie(
            name,
            path=path,
            httponly=httponly,
            **common,
        )
