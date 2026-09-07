"""Application settings with validation."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    app_name: str = "PodSight"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, description="Enable debug mode")

    port: int = Field(default=3000, ge=1, le=65535)
    host: str = Field(default="0.0.0.0")

    telemetry_timeout_seconds: float = Field(default=5.0, gt=0)
    telemetry_max_retries: int = Field(default=3, ge=0)
    telemetry_retry_backoff_base: float = Field(default=0.5, gt=0)

    cost_adapter_timeout_seconds: float = Field(default=10.0, gt=0)
    cost_adapter_max_retries: int = Field(default=3, ge=0)
    cost_adapter_retry_backoff_base: float = Field(default=1.0, gt=0)

    database_url: Optional[str] = Field(default=None)
    redis_url: Optional[str] = Field(default=None)

    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()