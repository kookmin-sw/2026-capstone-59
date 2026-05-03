from abc import ABC, abstractmethod
from typing import Any, ClassVar

import httpx

from app.core.exceptions import OAuthAuthorizationError
from app.core.schemas.auth import OAuthTokens, OAuthUserInfo

_HTTP_TIMEOUT_SECONDS = 10.0


class OAuthProviderClient(ABC):
    """OAuth 제공자 공통 인터페이스."""

    name: ClassVar[str]

    label: ClassVar[str]

    @abstractmethod
    def get_authorization_url(self, state: str | None = None) -> str:
        """OAuth 인증 페이지 URL 생성."""

    @abstractmethod
    def exchange_code(self, code: str, state: str | None = None) -> OAuthTokens:
        """Authorization Code → Access Token 교환."""

    @abstractmethod
    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Access Token으로 사용자 정보 조회."""

    # === 공통 HTTP 헬퍼 ===

    def _post_form(self, url: str, data: dict[str, Any], action: str) -> dict[str, Any]:
        """form-urlencoded POST → JSON 응답. 실패 시 OAuthAuthorizationError로 변환."""
        try:
            with httpx.Client(timeout=_HTTP_TIMEOUT_SECONDS) as client:
                resp = client.post(url, data=data)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            raise OAuthAuthorizationError(f"{self.label} {action} 실패: {e}")

    def _get_with_token(
        self, url: str, access_token: str, action: str
    ) -> dict[str, Any]:
        """Bearer 인증 GET → JSON 응답. 실패 시 OAuthAuthorizationError로 변환."""
        try:
            with httpx.Client(timeout=_HTTP_TIMEOUT_SECONDS) as client:
                resp = client.get(
                    url, headers={"Authorization": f"Bearer {access_token}"}
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            raise OAuthAuthorizationError(f"{self.label} {action} 실패: {e}")
