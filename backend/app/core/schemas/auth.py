from uuid import UUID

from pydantic import BaseModel


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserProfileResponse(BaseModel):
    user_id: UUID
    email: str
    nickname: str
    provider: str


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
