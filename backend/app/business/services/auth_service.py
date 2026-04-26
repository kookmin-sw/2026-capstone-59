from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.business.auth.providers import get_provider
from app.core.auth.jwt import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.core.exceptions import UserNotFoundError
from app.core.models.app_user import AppUser as AppUserModel
from app.core.models.oauth_account import OAuthAccount as OAuthAccountModel
from app.core.schemas.auth import (
    AuthTokenResponse,
    OAuthTokens,
    OAuthUserInfo,
    UserProfileResponse,
)


def get_authorization_url(provider_name: str, state: str | None = None) -> str:
    provider = get_provider(provider_name)
    return provider.get_authorization_url(state=state)


def handle_oauth_callback(db: Session, provider_name: str, code: str) -> AuthTokenResponse:
    """OAuth 콜백 처리: code → 사용자 조회/생성 → JWT 발급."""
    provider = get_provider(provider_name)

    oauth_tokens = provider.exchange_code(code)
    user_info = provider.get_user_info(oauth_tokens.access_token)

    user = _get_or_create_user(db, provider_name, user_info, oauth_tokens)
    return _issue_tokens(user)


def refresh_access_token(refresh_token: str) -> AuthTokenResponse:
    user_id = decode_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    return AuthTokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def get_user_profile(db: Session, user: AppUserModel) -> UserProfileResponse:
    oauth = (
        db.query(OAuthAccountModel)
        .filter(OAuthAccountModel.user_id == user.id)
        .first()
    )
    return UserProfileResponse(
        user_id=user.id,
        email=user.email,
        nickname=user.nickname,
        provider=oauth.provider if oauth else "",
    )


def _get_or_create_user(
    db: Session,
    provider_name: str,
    user_info: OAuthUserInfo,
    oauth_tokens: OAuthTokens,
) -> AppUserModel:
    oauth = (
        db.query(OAuthAccountModel)
        .filter(
            OAuthAccountModel.provider == provider_name,
            OAuthAccountModel.provider_user_id == user_info.provider_user_id,
        )
        .first()
    )

    expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=oauth_tokens.expires_in)
        if oauth_tokens.expires_in
        else None
    )

    if oauth:
        oauth.access_token = oauth_tokens.access_token
        if oauth_tokens.refresh_token:
            oauth.refresh_token = oauth_tokens.refresh_token
        oauth.token_expires_at = expires_at
        db.commit()

        user = db.get(AppUserModel, oauth.user_id)
        if not user or user.is_deleted:
            raise UserNotFoundError()
        return user

    # 신규 사용자 생성
    user = AppUserModel(
        email=user_info.email,
        nickname=user_info.nickname,
    )
    db.add(user)
    db.flush()

    oauth = OAuthAccountModel(
        user_id=user.id,
        provider=provider_name,
        provider_user_id=user_info.provider_user_id,
        access_token=oauth_tokens.access_token,
        refresh_token=oauth_tokens.refresh_token,
        token_expires_at=expires_at,
    )
    db.add(oauth)
    db.commit()
    db.refresh(user)
    return user


def _issue_tokens(user: AppUserModel) -> AuthTokenResponse:
    return AuthTokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
