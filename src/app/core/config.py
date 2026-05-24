from __future__ import annotations

from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MiraiGo"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "miraigo"
    DATABASE_URL: str | None = None

    REDIS_URL: str | None = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    SEARCH_CACHE_TTL_SECONDS: int = 900
    PROVIDER_TIMEOUT_SECONDS: float = 12.0
    PROVIDER_MAX_RETRIES: int = 2

    DEFAULT_CURRENCY_CODE: str = "USD"
    DUFFEL_API_URL: str = "https://api.duffel.com"
    DUFFEL_API_VERSION: str = "v2"
    DUFFEL_ACCESS_TOKEN: str | None = None
    DUFFEL_SUPPLIER_TIMEOUT_MS: int = 12000
    AMADEUS_API_URL: str = "https://test.api.amadeus.com"
    AMADEUS_CLIENT_ID: str | None = None
    AMADEUS_CLIENT_SECRET: str | None = None
    AMADEUS_REQUEST_DEADLINE_SECONDS: float = 10.0
    AMADEUS_TOKEN_SAFETY_BUFFER_SECONDS: int = 60
    AMADEUS_TOKEN_CACHE_KEY: str = "providers:amadeus:oauth-token"
    ENABLE_LLM_SUGGESTIONS: bool = False
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore",
    )

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def get_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def cors_origins(self) -> list[str]:
        return [self.FRONTEND_ORIGIN, "http://localhost:3000"]


settings = Settings()
