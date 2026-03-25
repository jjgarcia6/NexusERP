from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MovementTypeEnum(str, Enum):
    purchase_entry = "purchase_entry"
    sale_exit = "sale_exit"
    manual_entry = "manual_entry"
    manual_exit = "manual_exit"
    adjustment = "adjustment"


MANUAL_MOVEMENT_TYPES = {
    MovementTypeEnum.manual_entry,
    MovementTypeEnum.manual_exit,
    MovementTypeEnum.adjustment,
}


class StockInitRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    quantity: int = Field(
        ge=0,
        description=(
            "Cantidad inicial de stock. Cero es valido para registrar " "un producto sin unidades."
        ),
    )
    min_stock: int = Field(
        default=0,
        ge=0,
        description="Umbral minimo de alerta. Si available_quantity < min_stock, low_stock = true.",
    )


class StockLevelResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    product_id: str = Field(description="ID del producto asociado al nivel de stock.")
    product_name: str = Field(description="Nombre desnormalizado del producto.")
    available_quantity: int = Field(description="Cantidad disponible actual. Nunca negativa.")
    min_stock: int = Field(description="Umbral minimo de alerta para el producto.")
    low_stock: bool = Field(description="Indicador calculado de alerta por stock bajo.")
    updated_at: datetime = Field(description="Fecha de ultima actualizacion del nivel de stock.")


class StockListResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    items: list[StockLevelResponse] = Field(
        description="Lista de niveles de stock de la pagina actual.",
    )
    total: int = Field(description="Total de registros que coinciden con el filtro.")
    skip: int = Field(description="Numero de registros omitidos en paginacion.")
    limit: int = Field(description="Maximo numero de registros por pagina.")


class StockMovementRequest(BaseModel):
    # Allow enum values sent as JSON strings from API clients.
    model_config = ConfigDict(strict=False)

    product_id: str = Field(description="ID del producto con stock inicializado.")
    type: MovementTypeEnum = Field(
        description="Tipo de movimiento solicitado. Solo se permiten tipos manuales.",
    )
    quantity: int = Field(
        description="Cantidad del movimiento. Puede ser negativa solo para adjustment.",
    )
    reason: str | None = Field(
        default=None,
        min_length=5,
        max_length=300,
        description="Motivo del movimiento. Obligatorio para todos los tipos manuales.",
    )

    @model_validator(mode="after")
    def validate_manual_type_and_reason(self) -> StockMovementRequest:
        if self.type not in MANUAL_MOVEMENT_TYPES:
            raise ValueError(f"Solo se permiten movimientos manuales. Tipo recibido: {self.type}")

        if self.reason is None or not self.reason.strip():
            raise ValueError("El motivo es obligatorio para movimientos manuales y ajustes.")

        return self


class StockMovementResponse(BaseModel):
    model_config = ConfigDict(strict=False)

    id: str = Field(description="Identificador unico del movimiento.")
    product_id: str = Field(description="ID del producto afectado por el movimiento.")
    product_name: str = Field(
        description="Nombre historico del producto al momento del movimiento.",
    )
    type: MovementTypeEnum = Field(description="Tipo del movimiento registrado.")
    quantity: int = Field(description="Cantidad de unidades del movimiento.")
    quantity_before: int = Field(description="Stock disponible antes del movimiento.")
    quantity_after: int = Field(description="Stock disponible despues del movimiento.")
    reason: str | None = Field(description="Motivo informado para el movimiento.")
    reference_id: str | None = Field(description="ID de la referencia asociada (orden/venta).")
    reference_type: str | None = Field(description="Tipo de referencia asociada al movimiento.")
    created_at: datetime = Field(description="Fecha de registro del movimiento en UTC.")


class StockMovementListResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    items: list[StockMovementResponse] = Field(
        description="Lista paginada de movimientos de stock.",
    )
    total: int = Field(description="Total de movimientos que coinciden con el filtro.")
    skip: int = Field(description="Numero de movimientos omitidos en paginacion.")
    limit: int = Field(description="Maximo numero de movimientos por pagina.")
