from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_url: str = Field(description="URL de conexión a MongoDB Atlas.")
    mongodb_db_name: str = Field(description="Nombre de la base de datos activa.")
    app_env: Literal["development", "staging", "production"] = Field(
        description="Entorno de ejecución de la aplicación.",
    )
    app_cors_origins: str = Field(
        description="Orígenes permitidos para CORS separados por coma.",
    )
    jwt_secret_key: str = Field(description="Clave secreta para firmar tokens JWT.")
    jwt_algorithm: str = Field(description="Algoritmo de firma JWT.")
    jwt_access_token_expire_minutes: int = Field(
        description="Minutos de validez para access token.",
    )
    jwt_refresh_token_expire_days: int = Field(
        description="Días de validez para refresh token.",
    )
    jwt_refresh_cookie_secure: bool = Field(
        description="Define si la cookie refresh usa la bandera Secure.",
    )

    model_config = SettingsConfigDict(env_file=".env", strict=True, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
