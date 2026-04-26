from abc import ABC, abstractmethod

from app.core.schemas.auth import OAuthTokens, OAuthUserInfo


class OAuthProviderClient(ABC):
    """OAuth 제공자 공통 인터페이스."""

    @property
    @abstractmethod
    def name(self) -> str:
        """provider 이름 (google | naver | kakao)."""

    @abstractmethod
    def get_authorization_url(self, state: str | None = None) -> str:
        """OAuth 인증 페이지 URL 생성."""

    @abstractmethod
    def exchange_code(self, code: str) -> OAuthTokens:
        """Authorization Code → Access Token 교환."""

    @abstractmethod
    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Access Token으로 사용자 정보 조회."""
