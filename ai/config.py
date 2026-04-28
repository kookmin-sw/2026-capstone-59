"""환경 변수 기반 AI 모듈 설정.

backend 의존성 없이 독립 동작하며, pydantic-settings로 환경 변수를 로드한다.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """AI 모듈 환경 설정.

    환경 변수 또는 .env 파일에서 값을 로드한다.
    모든 필드에 sensible default가 있으므로 최소 설정으로 동작 가능.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    AWS_REGION: str = "us-east-1"
    MODEL_ID: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    KB_ID: str = ""
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7


ai_settings = AISettings()
