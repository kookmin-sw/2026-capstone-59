from uuid import UUID

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.core.auth.jwt import ACCESS_TOKEN_TYPE, decode_token
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import InvalidTokenError, UserNotFoundError
from app.core.models.app_user import AppUser as AppUserModel
from app.core.repositories import user as user_repo


def get_current_user_id(
    access_token: str | None = Cookie(default=None, alias=settings.ACCESS_COOKIE_NAME),
) -> UUID:
    """access_token 쿠키를 검증하고 user_id만 추출.
    DB 조회가 필요 없는 경우(AI Lambda 등) 사용."""
    if not access_token:
        raise InvalidTokenError("Access Token 쿠키가 없습니다.")
    return decode_token(access_token, expected_type=ACCESS_TOKEN_TYPE)


def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> AppUserModel:
    """JWT 검증 + DB에서 AppUser 조회. is_deleted 체크."""
    user = user_repo.get_active_user(db, user_id)
    if not user:
        raise UserNotFoundError()
    return user
