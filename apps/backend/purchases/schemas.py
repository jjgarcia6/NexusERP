from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrderStatusEnum(str, Enum):
    draft = "draft"
    confirmed = "confirmed"
    received = "received"
    cancelled = "cancelled"


class SupplierRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(
        min_length=2,
        max_length=150,
        description="Nombre comercial o razon social del proveedor.",
    )
    ruc: str | None = Field(
        default=None,
        max_length=13,
        description="RUC del proveedor. Unico cuando se provee.",
    )
    contact_name: str | None = Field(
        default=None,
        max_length=100,
        description="Nombre de la persona de contacto. PII potencial bajo LOPDP.",
    )
    contact_email: EmailStr | None = Field(
        default=None,
        description="Email de contacto. PII potencial bajo LOPDP.",
    )
    contact_phone: str | None = Field(
        default=None,
        max_length=20,
        description="Telefono de contacto del proveedor.",
    )
    address: str | None = Field(
        default=None,
        max_length=300,
        description="Direccion del proveedor.",
    )


class SupplierResponse(SupplierRequest):
    model_config = ConfigDict(strict=True)

    id: str = Field(description="Identificador unico del proveedor.")
    is_active: bool = Field(description="Estado del proveedor. false = soft delete.")
    created_at: datetime = Field(description="Fecha de creacion en UTC.")
    updated_at: datetime = Field(description="Fecha de ultima modificacion en UTC.")


class SupplierUpdateRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Nuevo nombre comercial o razon social.",
    )
    ruc: str | None = Field(
        default=None,
        max_length=13,
        description="Nuevo RUC del proveedor.",
    )
    contact_name: str | None = Field(
        default=None,
        max_length=100,
        description="Nuevo nombre de contacto.",
    )
    contact_email: EmailStr | None = Field(
        default=None,
        description="Nuevo email de contacto.",
    )
    contact_phone: str | None = Field(
        default=None,
        max_length=20,
        description="Nuevo telefono de contacto.",
    )
    address: str | None = Field(
        default=None,
        max_length=300,
        description="Nueva direccion.",
    )
    is_active: bool | None = Field(
        default=None,
        description="Nuevo estado. false = soft delete.",
    )


class PurchaseOrderLineRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    product_id: str = Field(
        description="ID del producto. Debe existir en products con is_active true.",
    )
    quantity: int = Field(
        gt=0,
        description="Cantidad de unidades. Entero positivo minimo 1.",
    )
    unit_cost: Decimal = Field(
        gt=0,
        strict=False,
        decimal_places=2,
        description="Precio unitario de compra acordado con el proveedor.",
    )


class PurchaseOrderLineResponse(PurchaseOrderLineRequest):
    model_config = ConfigDict(strict=True)

    product_name: str = Field(
        description="Nombre del producto desnormalizado al crear la orden.",
    )
    subtotal: Decimal = Field(
        gt=0,
        strict=False,
        decimal_places=2,
        description="Subtotal calculado: quantity por unit_cost.",
    )


class PurchaseOrderRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    supplier_id: str = Field(
        description="ID del proveedor. Debe existir y tener is_active true.",
    )
    lines: list[PurchaseOrderLineRequest] = Field(
        min_length=1,
        description="Lineas de detalle. Minimo una linea requerida.",
    )
    notes: str | None = Field(
        default=None,
        max_length=500,
        description="Notas internas sobre la orden.",
    )


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    id: str = Field(description="Identificador unico de la orden.")
    supplier_id: str = Field(description="ID del proveedor.")
    supplier_name: str = Field(
        description="Nombre del proveedor desnormalizado al crear la orden.",
    )
    status: OrderStatusEnum = Field(description="Estado actual de la orden.")
    lines: list[PurchaseOrderLineResponse] = Field(
        description="Lineas de detalle con subtotales calculados.",
    )
    total: Decimal = Field(
        gt=0,
        strict=False,
        decimal_places=2,
        description="Total de la orden suma de subtotales de todas las lineas.",
    )
    notes: str | None = Field(
        default=None,
        description="Notas internas de la orden.",
    )
    confirmed_at: datetime | None = Field(
        default=None,
        description="Fecha de confirmacion en UTC. null si no confirmada.",
    )
    received_at: datetime | None = Field(
        default=None,
        description="Fecha de recepcion en UTC. null si no recibida.",
    )
    cancelled_at: datetime | None = Field(
        default=None,
        description="Fecha de cancelacion en UTC. null si no cancelada.",
    )
    created_at: datetime = Field(description="Fecha de creacion en UTC.")
    updated_at: datetime = Field(description="Fecha de ultima modificacion en UTC.")


class PurchaseOrderListResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    items: list[PurchaseOrderResponse] = Field(
        description="Lista de ordenes de la pagina actual.",
    )
    total: int = Field(
        ge=0,
        description="Total de ordenes que coinciden con los filtros aplicados.",
    )
    skip: int = Field(ge=0, description="Numero de documentos omitidos.")
    limit: int = Field(gt=0, description="Numero maximo de documentos retornados.")
