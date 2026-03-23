from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, cast

from fastapi import HTTPException, status
from jose import JWTError, jwt  # type: ignore[import-untyped]

from core.settings import get_settings


def _encode_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    settings = get_settings()
    payload = data.copy()
    payload["exp"] = datetime.now(UTC) + expires_delta
    encoded = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return cast(str, encoded)


def create_access_token(data: dict[str, Any]) -> str:
    settings = get_settings()
    return _encode_token(
        data,
        timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    settings = get_settings()
    return _encode_token(
        data,
        timedelta(days=settings.jwt_refresh_token_expire_days),
    )


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        decoded = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from exc

    if "sub" not in decoded or "role" not in decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    return cast(dict[str, Any], decoded)
