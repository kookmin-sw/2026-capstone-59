"""AppUser / OAuthAccount repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.models.app_user import AppUser
from app.core.models.oauth_account import OAuthAccount

# ── AppUser ────────────────────────────────────────────────────────────


def get_active_user(db: Session, user_id: UUID) -> AppUser | None:
    return (
        db.query(AppUser)
        .filter(AppUser.id == user_id, AppUser.is_deleted.is_(False))
        .first()
    )


def add_user(db: Session, *, email: str, nickname: str | None) -> AppUser:
    user = AppUser(email=email, nickname=nickname)
    db.add(user)
    db.flush()
    return user


# ── OAuthAccount ───────────────────────────────────────────────────────


def get_oauth_by_provider_and_user(
    db: Session, provider: str, provider_user_id: str
) -> OAuthAccount | None:
    return (
        db.query(OAuthAccount)
        .filter(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
        .first()
    )


def get_oauth_by_user_id(db: Session, user_id: UUID) -> OAuthAccount | None:
    return db.query(OAuthAccount).filter(OAuthAccount.user_id == user_id).first()


def add_oauth_account(
    db: Session,
    *,
    user_id: UUID,
    provider: str,
    provider_user_id: str,
    access_token: str | None,
    refresh_token: str | None,
    token_expires_at: datetime | None,
) -> OAuthAccount:
    account = OAuthAccount(
        user_id=user_id,
        provider=provider,
        provider_user_id=provider_user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        token_expires_at=token_expires_at,
    )
    db.add(account)
    return account


def update_oauth_tokens(
    account: OAuthAccount,
    *,
    access_token: str | None,
    refresh_token: str | None,
    token_expires_at: datetime | None,
) -> OAuthAccount:
    account.access_token = access_token
    if refresh_token:
        account.refresh_token = refresh_token
    account.token_expires_at = token_expires_at
    return account
