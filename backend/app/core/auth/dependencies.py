from uuid import UUID

from fastapi import Cookie, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.auth.jwt import ACCESS_TOKEN_TYPE, decode_token
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import InvalidTokenError, UserNotFoundError
from app.core.models.app_user import AppUser as AppUserModel
from app.core.repositories import user as user_repo

# Swagger UI 의 Authorize 버튼 활성화용. auto_error=False 라서
# 헤더 없으면 None 이 들어오고, 우리가 직접 쿠키 폴백 처리.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    access_token: str | None = Cookie(default=None, alias=settings.ACCESS_COOKIE_NAME),
    bearer: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> UUID:
    """access_token 을 검증하고 user_id만 추출.

    우선순위: Cookie → Authorization Bearer 헤더.
    AI Lambda 는 Function URL (별도 도메인) 으로 호출되어 쿠키가 안 가므로
    프론트가 Bearer 헤더로 폴백한다.
    """
    token = access_token or (bearer.credentials if bearer else None)
    if not token:
        raise InvalidTokenError("Access Token 이 없습니다.")
    return decode_token(token, expected_type=ACCESS_TOKEN_TYPE)


def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> AppUserModel:
    """JWT 검증 + DB에서 AppUser 조회. is_deleted 체크."""
    user = user_repo.get_active_user(db, user_id)
    if not user:
        raise UserNotFoundError()
    return user
