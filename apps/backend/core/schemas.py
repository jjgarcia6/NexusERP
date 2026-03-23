from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BaseResponse(BaseModel):
    model_config = ConfigDict(strict=True)


class HealthResponse(BaseResponse):
    status: Literal["ok"] = Field(
        default="ok",
        description="Confirma que el backend arrancó correctamente y puede comunicarse con Atlas.",
    )


class ServiceUnavailableResponse(BaseResponse):
    status: Literal["error"] = Field(
        default="error",
        description=(
            "Indica que el servicio está activo pero su dependencia " "de datos no está disponible."
        ),
    )
    detail: Literal["database unavailable"] = Field(
        default="database unavailable",
        description="Mensaje técnico controlado para indisponibilidad de la base de datos.",
    )
