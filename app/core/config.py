from functools import lru_cache
import os

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    ENV: str = "development"

    DATABASE_URL: str | None = None
    REDIS_URL: str

    DEBUG: bool = False

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    RATE_LIMIT_ENABLED: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_value(cls, value):
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()

            if normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production", "prod"}:
                return False

        return value


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

USE_ML_MODEL = os.getenv("USE_ML_MODEL", "false").lower() == "true"
