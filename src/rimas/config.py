"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://rimas:rimas@localhost:5432/rimas"
    database_url_async: str = "postgresql+asyncpg://rimas:rimas@localhost:5432/rimas"
    mlflow_tracking_uri: str = "http://localhost:5000"
    openai_api_key: str | None = None

    @property
    def has_llm(self) -> bool:
        return bool(self.openai_api_key)


settings = Settings()
