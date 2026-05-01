from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    # DB
    DB_HOST: str = "localhost"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "pocodb"
    DB_PORT: int = 5432
    DB_SSL: bool = False

    # AWS
    AWS_REGION: str = "ap-northeast-2"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_KB_ID: str = ""

    # Notion
    NOTION_TOKEN: str = ""

    # JWT
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    # Naver OAuth
    NAVER_CLIENT_ID: str = ""
    NAVER_CLIENT_SECRET: str = ""
    NAVER_REDIRECT_URI: str = ""

    # 프론트엔드 OAuth 콜백 URL
    FRONTEND_REDIRECT_URL: str = "http://localhost/auth/callback"

    # CORS (옵션 A: 프로덕션에서는 same-origin이라 비워두고, 개발에서만 명시)
    CORS_ALLOWED_ORIGINS: list[str] = []

    # Cookie
    COOKIE_SECURE: bool = True  # 개발 HTTP 환경에서는 false로 설정
    COOKIE_SAMESITE: str = "lax"  # same-site 가정
    COOKIE_DOMAIN: str | None = None  # None이면 현재 호스트 자동 적용
    ACCESS_COOKIE_NAME: str = "access_token"
    REFRESH_COOKIE_NAME: str = "refresh_token"
    CSRF_COOKIE_NAME: str = "csrf_token"
    CSRF_HEADER_NAME: str = "X-CSRF-Token"

    @property
    def DATABASE_URL(self) -> str:
        url = (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        if self.DB_SSL:
            url += "?sslmode=require"
        return url


settings = Settings()
