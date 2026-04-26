from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.auth.jwt import ACCESS_TOKEN_TYPE, decode_token
from app.core.database import get_db
from app.core.exceptions import InvalidTokenError, UserNotFoundError
from app.core.models.app_user import AppUser as AppUserModel


def get_current_user_id(authorization: str | None = Header(default=None)) -> UUID:
    """Authorization 헤더에서 Bearer 토큰을 검증하고 user_id만 추출.
    DB 조회가 필요 없는 경우(AI Lambda 등) 사용."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise InvalidTokenError("Authorization 헤더가 누락되었거나 형식이 올바르지 않습니다.")
    token = authorization.split(" ", 1)[1].strip()
    return decode_token(token, expected_type=ACCESS_TOKEN_TYPE)


def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> AppUserModel:
    """JWT 검증 + DB에서 AppUser 조회. is_deleted 체크."""
    user = (
        db.query(AppUserModel)
        .filter(
            AppUserModel.id == user_id,
            AppUserModel.is_deleted == False,
        )
        .first()
    )
    if not user:
        raise UserNotFoundError()
    return user
