import secrets
from urllib.parse import urlencode

import httpx

from app.business.auth.providers.base import OAuthProviderClient
from app.core.config import settings
from app.core.enums import OAuthProvider
from app.core.exceptions import OAuthAuthorizationError
from app.core.schemas.auth import OAuthTokens, OAuthUserInfo

NAVER_AUTH_URL = "https://nid.naver.com/oauth2.0/authorize"
NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_USERINFO_URL = "https://openapi.naver.com/v1/nid/me"


class NaverOAuthProvider(OAuthProviderClient):
    @property
    def name(self) -> str:
        return OAuthProvider.NAVER.value

    def get_authorization_url(self, state: str | None = None) -> str:
        # 네이버는 state 파라미터가 필수. 호출자가 안 넘기면 안전한 랜덤값으로 자동 생성.
        params = {
            "response_type": "code",
            "client_id": settings.NAVER_CLIENT_ID,
            "redirect_uri": settings.NAVER_REDIRECT_URI,
            "state": state or secrets.token_urlsafe(16),
        }
        return f"{NAVER_AUTH_URL}?{urlencode(params)}"

    def exchange_code(self, code: str) -> OAuthTokens:
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    NAVER_TOKEN_URL,
                    data={
                        "grant_type": "authorization_code",
                        "client_id": settings.NAVER_CLIENT_ID,
                        "client_secret": settings.NAVER_CLIENT_SECRET,
                        "code": code,
                        # 네이버는 토큰 교환 시에도 state를 요구하지만, 별도 검증을 하지 않으므로
                        # 자리 채움용 임의값을 보내도 무방하다.
                        "state": "exchange",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            raise OAuthAuthorizationError(f"Naver 토큰 교환 실패: {e}")

        # 네이버 에러 응답은 200으로 오면서 본문에 error 필드를 담아 반환하기도 함.
        if "error" in data:
            raise OAuthAuthorizationError(
                f"Naver 토큰 교환 실패: {data.get('error_description') or data['error']}"
            )

        expires_in = data.get("expires_in")
        return OAuthTokens(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=int(expires_in) if expires_in is not None else None,
        )

    def get_user_info(self, access_token: str) -> OAuthUserInfo:
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    NAVER_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            raise OAuthAuthorizationError(f"Naver 사용자 정보 조회 실패: {e}")

        # 네이버 응답 형식: {"resultcode": "00", "message": "success", "response": {...}}
        if data.get("resultcode") != "00":
            raise OAuthAuthorizationError(
                f"Naver 사용자 정보 조회 실패: {data.get('message')}"
            )

        profile = data.get("response") or {}
        email = profile.get("email", "")
        nickname = (
            profile.get("nickname")
            or profile.get("name")
            or (email.split("@")[0] if email else "")
        )
        return OAuthUserInfo(
            provider_user_id=str(profile["id"]),
            email=email,
            nickname=nickname,
        )
