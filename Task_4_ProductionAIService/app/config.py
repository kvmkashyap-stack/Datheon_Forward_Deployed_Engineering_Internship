
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "production-ai-service"
    app_env: Literal["development", "test", "production"] = "development"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: str = "INFO"

    ai_provider: str = "mock"
    ai_api_key: SecretStr | None = None
    ai_model: str = ""

    request_timeout_seconds: float = Field(default=30, gt=0, le=300)
    max_request_size_bytes: int = Field(
        default=1_048_576, gt=0, le=10_485_760
    )
    metrics_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
