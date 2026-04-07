from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SaleStatusEnum(str, Enum):
    draft = "draft"
    confirmed = "confirmed"
    cancelled = "cancelled"


class PaymentMethodEnum(str, Enum):
    cash = "cash"
    card = "card"
    transfer = "transfer"


TAX_RATE = Decimal("0.12")  # IVA Ecuador — constante, no campo de usuario


class SaleLineRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    product_id: str = Field(..., description="ID del producto. DEBE existir con is_active: true.")
    quantity: int = Field(
        ..., gt=0, description="Cantidad de unidades vendidas. Entero positivo mínimo 1."
    )


class SaleLineResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    product_id: str = Field(description="ID del producto en la línea.")
    product_name: str = Field(description="Nombre histórico del producto.")
    quantity: int = Field(description="Cantidad vendida.")
    unit_price: Decimal = Field(
        decimal_places=2, description="Precio unitario al momento de la venta."
    )
    subtotal: Decimal = Field(decimal_places=2, description="Subtotal: quantity × unit_price.")


class SaleRequest(BaseModel):
    # HTTP JSON sends enums as strings (e.g. "cash"), so request parsing must be non-strict.
    model_config = ConfigDict(strict=False)
    customer_id: str = Field(..., description="ID del cliente. DEBE existir con is_active: true.")
    payment_method: PaymentMethodEnum = Field(..., description="Método de pago de la venta.")
    lines: list[SaleLineRequest] = Field(
        ..., min_length=1, description="Líneas de la venta. Mínimo 1 línea requerida."
    )
    notes: str | None = Field(
        default=None, max_length=500, description="Notas internas de la venta."
    )


class SaleResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str = Field(description="Identificador único de la venta.")
    customer_id: str = Field(description="ID del cliente.")
    customer_name: str = Field(description="Nombre del cliente — histórico.")
    customer_identification: str = Field(
        description="Identificación del cliente — histórico. Requerido para comprobante."
    )
    status: SaleStatusEnum = Field(description="Estado actual de la venta.")
    invoice_number: str | None = Field(description="Número de comprobante. Null en draft.")
    payment_method: PaymentMethodEnum = Field(description="Método de pago.")
    lines: list[SaleLineResponse] = Field(description="Líneas de la venta.")
    subtotal_before_tax: Decimal = Field(decimal_places=2, description="Subtotal antes de IVA.")
    tax_rate: Decimal = Field(decimal_places=2, description="Tasa de IVA aplicada. Siempre 0.12.")
    tax_amount: Decimal = Field(decimal_places=2, description="Monto de IVA.")
    total: Decimal = Field(decimal_places=2, description="Total a cobrar.")
    notes: str | None = Field(description="Notas internas.")
    confirmed_at: datetime | None = Field(description="Fecha de confirmación.")
    cancelled_at: datetime | None = Field(description="Fecha de cancelación.")
    created_at: datetime = Field(description="Fecha de creación en UTC.")
    updated_at: datetime = Field(description="Fecha de última modificación.")


class SaleListResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    items: list[SaleResponse] = Field(description="Lista de ventas.")
    total: int = Field(description="Total de ventas con los filtros aplicados.")
    skip: int = Field(description="Número de documentos omitidos.")
    limit: int = Field(description="Número máximo de documentos retornados.")
