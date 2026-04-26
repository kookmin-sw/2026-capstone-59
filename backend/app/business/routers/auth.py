from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.business.dependency import get_db
from app.business.services import auth_service
from app.core.auth.dependencies import get_current_user
from app.core.config import settings
from app.core.models.app_user import AppUser as AppUserModel
from app.core.schemas.auth import TokenRefreshRequest

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data}


@router.get("/{provider}/login")
def oauth_login(provider: str, state: str | None = Query(default=None)):
    """OAuth 인증 페이지로 리다이렉트."""
    url = auth_service.get_authorization_url(provider, state=state)
    return RedirectResponse(url=url, status_code=http_status.HTTP_302_FOUND)


@router.get("/{provider}/callback")
def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """OAuth Provider 콜백 — code를 토큰으로 교환 후 프론트로 리다이렉트.
    토큰은 URL fragment(#)에 담아 전달 (서버 로그 노출 방지)."""
    tokens = auth_service.handle_oauth_callback(db, provider, code)
    fragment = urlencode(
        {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": tokens.expires_in,
        }
    )
    return RedirectResponse(
        url=f"{settings.FRONTEND_REDIRECT_URL}#{fragment}",
        status_code=http_status.HTTP_302_FOUND,
    )


@router.post("/refresh", status_code=http_status.HTTP_200_OK)
def refresh_token(payload: TokenRefreshRequest):
    """Refresh Token으로 Access Token 갱신."""
    return _ok(auth_service.refresh_access_token(payload.refresh_token).model_dump())


@router.post("/logout", status_code=http_status.HTTP_200_OK)
def logout(_: AppUserModel = Depends(get_current_user)):
    """로그아웃 — Stateless JWT라 클라이언트가 토큰 폐기.
    추후 token blacklist를 추가하려면 여기에서 처리."""
    return _ok(None)


@router.get("/me", status_code=http_status.HTTP_200_OK)
def get_me(
    user: AppUserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """현재 로그인 사용자 정보."""
    return _ok(auth_service.get_user_profile(db, user).model_dump())
