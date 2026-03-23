from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from pymongo.errors import PyMongoError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class _HealthyDatabase:
    async def command(self, _: str) -> dict[str, int]:
        return {"ok": 1}


class _UnavailableDatabase:
    async def command(self, _: str) -> dict[str, int]:
        raise PyMongoError("database unavailable")


@pytest.mark.asyncio
async def test_health_returns_200_when_database_is_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGODB_DB_NAME", "nexuserp")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("APP_CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    monkeypatch.setenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    monkeypatch.setenv("JWT_REFRESH_COOKIE_SECURE", "false")

    module = importlib.import_module("main")
    router_module = importlib.import_module("routers.health_router")
    monkeypatch.setattr(router_module, "get_database", lambda: _HealthyDatabase())

    async with AsyncClient(
        transport=ASGITransport(app=module.app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_returns_503_when_database_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGODB_DB_NAME", "nexuserp")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("APP_CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    monkeypatch.setenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    monkeypatch.setenv("JWT_REFRESH_COOKIE_SECURE", "false")

    module = importlib.import_module("main")
    router_module = importlib.import_module("routers.health_router")
    monkeypatch.setattr(router_module, "get_database", lambda: _UnavailableDatabase())

    async with AsyncClient(
        transport=ASGITransport(app=module.app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "error",
        "detail": "database unavailable",
    }


def test_settings_fails_when_mongodb_url_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MONGODB_URL", raising=False)
    monkeypatch.setenv("MONGODB_DB_NAME", "nexuserp")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("APP_CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    monkeypatch.setenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    monkeypatch.setenv("JWT_REFRESH_COOKIE_SECURE", "false")

    settings_module = importlib.import_module("core.settings")
    settings_module.get_settings.cache_clear()

    with pytest.raises(ValidationError) as error:
        settings_module.Settings(_env_file=None)

    assert "mongodb_url" in str(error.value)
