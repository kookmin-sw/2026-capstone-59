from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    DB_HOST: str = "localhost"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "pocodb"
    DB_PORT: int = 5432
    DB_SSL: bool = False

    AWS_REGION: str = "ap-northeast-2"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_KB_ID: str = ""

    NOTION_TOKEN: str = ""

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
