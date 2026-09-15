from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Servicios upstream
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    AFILIADOS_SERVICE_URL: str = "http://localhost:8002"

    # Aplicación
    APP_NAME: str = "API Gateway"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
