from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException


def _parse_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Formato de fecha invalido: {value}",
        ) from exc

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC)


def parse_period(from_str: str, to_str: str) -> tuple[datetime, datetime]:
    from_date = _parse_iso_datetime(from_str)
    to_date = _parse_iso_datetime(to_str)

    if from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail="Rango de fechas invalido: from no puede ser mayor que to.",
        )

    return from_date, to_date


def get_default_period() -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start_of_day, end_of_day
