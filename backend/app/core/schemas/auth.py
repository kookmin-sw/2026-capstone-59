from uuid import UUID

from pydantic import BaseModel


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class UserProfileResponse(BaseModel):
    user_id: UUID
    email: str
    nickname: str
    provider: str
    csrf_token: str | None = None
    # AI Lambda 의 Function URL 호출용 — 별도 도메인이라 쿠키가 안 가서
    # 프론트가 Authorization: Bearer 로 보낼 수 있도록 body 로도 노출.
    access_token: str | None = None


class CsrfTokenResponse(BaseModel):
    csrf_token: str
    access_token: str | None = None


class OAuthUserInfo(BaseModel):
    """OAuth Provider에서 가져온 사용자 정보 (내부용)."""

    provider_user_id: str
    email: str
    nickname: str


class OAuthTokens(BaseModel):
    """OAuth Provider의 토큰 (내부용)."""

    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None
