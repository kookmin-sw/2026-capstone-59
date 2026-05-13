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
from app.core.logging import get_logger
from app.core.models.app_user import AppUser as AppUserModel
from app.core.repositories import user as user_repo

logger = get_logger(__name__)
from app.core.schemas.auth import (
    AuthTokenResponse,
    OAuthTokens,
    OAuthUserInfo,
    UserProfileResponse,
)


def get_authorization_url(provider_name: str, state: str | None = None) -> str:
    provider = get_provider(provider_name)
    return provider.get_authorization_url(state=state)


def handle_oauth_callback(
    db: Session, provider_name: str, code: str, state: str | None = None
) -> AuthTokenResponse:
    """OAuth 콜백 처리: code → 사용자 조회/생성 → JWT 발급."""
    logger.debug("oauth: callback received", extra={"provider": provider_name})
    provider = get_provider(provider_name)

    try:
        oauth_tokens = provider.exchange_code(code, state=state)
        user_info = provider.get_user_info(oauth_tokens.access_token)
    except Exception:
        logger.error(
            "oauth: provider exchange failed",
            extra={"provider": provider_name},
            exc_info=True,
        )
        raise

    user = _get_or_create_user(db, provider_name, user_info, oauth_tokens)
    tokens = _issue_tokens(user)
    logger.info(
        "auth: login completed",
        extra={"user_id": str(user.id), "provider": provider_name},
    )
    return tokens


def refresh_access_token(refresh_token: str) -> AuthTokenResponse:
    user_id = decode_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    logger.info("auth: token refreshed", extra={"user_id": str(user_id)})
    return AuthTokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def get_user_profile(db: Session, user: AppUserModel) -> UserProfileResponse:
    oauth = user_repo.get_oauth_by_user_id(db, user.id)
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
    expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=oauth_tokens.expires_in)
        if oauth_tokens.expires_in
        else None
    )

    oauth = user_repo.get_oauth_by_provider_and_user(
        db, provider_name, user_info.provider_user_id
    )

    if oauth:
        user_repo.update_oauth_tokens(
            oauth,
            access_token=oauth_tokens.access_token,
            refresh_token=oauth_tokens.refresh_token,
            token_expires_at=expires_at,
        )
        db.commit()

        user = user_repo.get_active_user(db, oauth.user_id)
        if not user:
            logger.error(
                "auth: linked user not found",
                extra={
                    "provider": provider_name,
                    "oauth_user_id": str(oauth.user_id),
                },
            )
            raise UserNotFoundError()
        return user

    # 신규 사용자 생성
    user = user_repo.add_user(db, email=user_info.email, nickname=user_info.nickname)
    user_repo.add_oauth_account(
        db,
        user_id=user.id,
        provider=provider_name,
        provider_user_id=user_info.provider_user_id,
        access_token=oauth_tokens.access_token,
        refresh_token=oauth_tokens.refresh_token,
        token_expires_at=expires_at,
    )
    db.commit()
    db.refresh(user)
    logger.info(
        "auth: user signed up",
        extra={"user_id": str(user.id), "provider": provider_name},
    )
    return user


def _issue_tokens(user: AppUserModel) -> AuthTokenResponse:
    return AuthTokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
