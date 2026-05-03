from urllib.parse import urlencode

from app.business.auth.providers.base import OAuthProviderClient
from app.core.config import settings
from app.core.enums import OAuthProvider
from app.core.schemas.auth import OAuthTokens, OAuthUserInfo

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleOAuthProvider(OAuthProviderClient):
    name = OAuthProvider.GOOGLE.value
    label = "Google"

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

    def exchange_code(self, code: str, state: str | None = None) -> OAuthTokens:
        data = self._post_form(
            GOOGLE_TOKEN_URL,
            {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            action="토큰 교환",
        )
        return OAuthTokens(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
        )

    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        data = self._get_with_token(
            GOOGLE_USERINFO_URL, access_token, action="사용자 정보 조회"
        )
        return OAuthUserInfo(
            provider_user_id=str(data["sub"]),
            email=data.get("email", ""),
            nickname=data.get("name") or data.get("email", "").split("@")[0],
        )
