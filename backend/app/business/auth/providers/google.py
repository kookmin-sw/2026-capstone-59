from urllib.parse import urlencode

import httpx

from app.business.auth.providers.base import OAuthProviderClient
from app.core.config import settings
from app.core.enums import OAuthProvider
from app.core.exceptions import OAuthAuthorizationError
from app.core.schemas.auth import OAuthTokens, OAuthUserInfo

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleOAuthProvider(OAuthProviderClient):
    @property
    def name(self) -> str:
        return OAuthProvider.GOOGLE.value

    def get_authorization_url(self, state: str | None = None) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        if state:
            params["state"] = state
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    def exchange_code(self, code: str) -> OAuthTokens:
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    GOOGLE_TOKEN_URL,
                    data={
                        "code": code,
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                        "grant_type": "authorization_code",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            raise OAuthAuthorizationError(f"Google 토큰 교환 실패: {e}")

        return OAuthTokens(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
        )

    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            raise OAuthAuthorizationError(f"Google 사용자 정보 조회 실패: {e}")

        return OAuthUserInfo(
            provider_user_id=str(data["sub"]),
            email=data.get("email", ""),
            nickname=data.get("name") or data.get("email", "").split("@")[0],
        )
