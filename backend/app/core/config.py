from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py 위치 기준으로 backend/.env를 절대경로로 지정
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/poco_db"

    AWS_REGION: str = "ap-northeast-2"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_KB_ID: str = ""

    NOTION_TOKEN: str = ""


settings = Settings()
