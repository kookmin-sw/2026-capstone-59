from app.business.auth.providers.base import OAuthProviderClient
from app.business.auth.providers.google import GoogleOAuthProvider
from app.core.enums import OAuthProvider
from app.core.exceptions import UnsupportedOAuthProviderError

_PROVIDERS: dict[OAuthProvider, OAuthProviderClient] = {
    OAuthProvider.GOOGLE: GoogleOAuthProvider(),
}


def get_provider(provider_name: str) -> OAuthProviderClient:
    try:
        provider = OAuthProvider(provider_name)
    except ValueError:
        raise UnsupportedOAuthProviderError(
            f"지원하지 않는 OAuth Provider입니다: {provider_name}"
        )
    if provider not in _PROVIDERS:
        raise UnsupportedOAuthProviderError(
            f"아직 구현되지 않은 OAuth Provider입니다: {provider_name}"
        )
    return _PROVIDERS[provider]
