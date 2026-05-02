from fastapi import Cookie, Depends, Query, Response
from fastapi import status as http_status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.business.services import auth_service
from app.core.api.route import EnvelopeRouter
from app.core.auth.cookies import (
    clear_auth_cookies,
    generate_csrf_token,
    set_auth_cookies,
)
from app.core.auth.dependencies import get_current_user
from app.core.config import settings
from app.core.exceptions import InvalidTokenError
from app.core.models.app_user import AppUser as AppUserModel
from app.core.schemas.auth import UserProfileResponse

router = EnvelopeRouter()


@router.get("/{provider}/login")
def oauth_login(
    provider: str, state: str | None = Query(default=None)
) -> RedirectResponse:
    """OAuth 인증 페이지로 리다이렉트."""
    url = auth_service.get_authorization_url(provider, state=state)
    return RedirectResponse(url=url, status_code=http_status.HTTP_302_FOUND)


@router.get("/{provider}/callback")
def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    tokens = auth_service.handle_oauth_callback(db, provider, code)
    csrf = generate_csrf_token()

    response = RedirectResponse(
        url=settings.FRONTEND_REDIRECT_URL,
        status_code=http_status.HTTP_302_FOUND,
    )
    set_auth_cookies(
        response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        csrf_token=csrf,
    )
    return response


@router.post("/refresh", status_code=http_status.HTTP_200_OK)
def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None, alias=settings.REFRESH_COOKIE_NAME
    ),
) -> None:
    """Refresh Token 쿠키로 Access Token 갱신. 응답 쿠키도 모두 갱신."""
    if not refresh_token:
        raise InvalidTokenError("Refresh Token 쿠키가 없습니다.")

    tokens = auth_service.refresh_access_token(refresh_token)
    csrf = generate_csrf_token()
    set_auth_cookies(
        response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        csrf_token=csrf,
    )
    return None


@router.post("/logout", status_code=http_status.HTTP_200_OK)
def logout(
    response: Response,
    _: AppUserModel = Depends(get_current_user),
) -> None:
    clear_auth_cookies(response)
    return None


@router.get("/me", status_code=http_status.HTTP_200_OK)
def get_me(
    user: AppUserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    """현재 로그인 사용자 정보."""
    return auth_service.get_user_profile(db, user)
