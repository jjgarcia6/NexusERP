from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from bson import ObjectId
from bson.decimal128 import Decimal128
from fastapi import HTTPException, status

from catalog.repositories.product_repository import ProductRepository
from purchases.repositories.purchase_order_repository import PurchaseOrderRepository
from purchases.repositories.supplier_repository import SupplierRepository
from purchases.schemas import (
    OrderStatusEnum,
    PurchaseOrderLineResponse,
    PurchaseOrderListResponse,
    PurchaseOrderRequest,
    PurchaseOrderResponse,
)
from purchases.services.inventory_stub_service import InventoryServiceProtocol


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


def _to_bson_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return Decimal128(value)
    if isinstance(value, list):
        return [_to_bson_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_bson_value(item) for key, item in value.items()}
    return value


def _build_transition_error(current_status: str, next_status: OrderStatusEnum) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Transicion de estado invalida: {current_status} -> {next_status.value}",
    )


def _to_order_response(document: dict[str, Any]) -> PurchaseOrderResponse:
    created_at = document.get("created_at")
    updated_at = document.get("updated_at")
    if not isinstance(created_at, datetime) or not isinstance(updated_at, datetime):
        raise TypeError("Invalid purchase order date fields")

    lines_raw = document.get("lines", [])
    lines: list[PurchaseOrderLineResponse] = []
    for line in lines_raw:
        lines.append(
            PurchaseOrderLineResponse(
                product_id=str(line["product_id"]),
                quantity=int(line["quantity"]),
                unit_cost=_to_decimal(line["unit_cost"]),
                product_name=str(line["product_name"]),
                subtotal=_to_decimal(line["subtotal"]),
            )
        )

    return PurchaseOrderResponse(
        id=str(document["_id"]),
        supplier_id=str(document["supplier_id"]),
        supplier_name=str(document["supplier_name"]),
        status=OrderStatusEnum(str(document["status"])),
        lines=lines,
        total=_to_decimal(document["total"]),
        notes=(str(document["notes"]) if document.get("notes") else None),
        confirmed_at=document.get("confirmed_at"),
        received_at=document.get("received_at"),
        cancelled_at=document.get("cancelled_at"),
        created_at=created_at,
        updated_at=updated_at,
    )


class PurchaseOrderService:
    def __init__(
        self,
        purchase_order_repository: PurchaseOrderRepository,
        supplier_repository: SupplierRepository,
        product_repository: ProductRepository,
        inventory_service: InventoryServiceProtocol,
    ) -> None:
        self.purchase_order_repository = purchase_order_repository
        self.supplier_repository = supplier_repository
        self.product_repository = product_repository
        self.inventory_service = inventory_service

    async def create_order(
        self, payload: PurchaseOrderRequest, *, created_by: str
    ) -> PurchaseOrderResponse:
        supplier = await self.supplier_repository.find_by_id(payload.supplier_id)
        if supplier is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El proveedor especificado no esta activo",
            )

        normalized_lines: list[dict[str, Any]] = []
        total = Decimal("0")
        for index, line in enumerate(payload.lines, start=1):
            product = await self.product_repository.find_by_id(line.product_id, is_active=True)
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"La linea {index} contiene un producto inactivo",
                )

            unit_cost = Decimal(line.unit_cost)
            subtotal = unit_cost * Decimal(line.quantity)
            total += subtotal
            normalized_lines.append(
                {
                    "product_id": ObjectId(line.product_id),
                    "product_name": str(product["name"]),
                    "quantity": line.quantity,
                    "unit_cost": unit_cost,
                    "subtotal": subtotal,
                }
            )

        payload_dict: dict[str, Any] = {
            "supplier_id": ObjectId(payload.supplier_id),
            "supplier_name": str(supplier["name"]),
            "status": OrderStatusEnum.draft.value,
            "lines": normalized_lines,
            "total": total,
            "notes": payload.notes,
            "created_by": ObjectId(created_by),
            "confirmed_at": None,
            "received_at": None,
            "cancelled_at": None,
        }

        created = await self.purchase_order_repository.create_order(_to_bson_value(payload_dict))
        return _to_order_response(created)

    async def list_orders(
        self,
        *,
        order_status: OrderStatusEnum | None,
        supplier_id: str | None,
        skip: int,
        limit: int,
    ) -> PurchaseOrderListResponse:
        items, total = await self.purchase_order_repository.find_all(
            status=order_status,
            supplier_id=supplier_id,
            skip=skip,
            limit=limit,
        )
        serialized = [_to_order_response(item) for item in items]
        return PurchaseOrderListResponse(items=serialized, total=total, skip=skip, limit=limit)

    async def get_order(self, order_id: str) -> PurchaseOrderResponse:
        order = await self.purchase_order_repository.find_by_id(order_id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada"
            )
        return _to_order_response(order)

    async def confirm_order(self, order_id: str) -> PurchaseOrderResponse:
        current = await self.purchase_order_repository.find_by_id(order_id)
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada"
            )

        current_status = str(current.get("status", ""))
        if current_status != OrderStatusEnum.draft.value:
            raise _build_transition_error(current_status, OrderStatusEnum.confirmed)

        updated = await self.purchase_order_repository.update_status(
            order_id,
            OrderStatusEnum.confirmed,
            "confirmed_at",
        )
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada"
            )
        return _to_order_response(updated)

    async def receive_order(self, order_id: str) -> PurchaseOrderResponse:
        current = await self.purchase_order_repository.find_by_id(order_id)
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada"
            )

        current_status = str(current.get("status", ""))
        if current_status != OrderStatusEnum.confirmed.value:
            raise _build_transition_error(current_status, OrderStatusEnum.received)

        try:
            await self.inventory_service.register_stock_entries(_to_order_response(current))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo actualizar el inventario. Intente nuevamente",
            ) from exc

        updated = await self.purchase_order_repository.update_status(
            order_id,
            OrderStatusEnum.received,
            "received_at",
        )
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada"
            )
        return _to_order_response(updated)

    async def cancel_order(self, order_id: str) -> PurchaseOrderResponse:
        current = await self.purchase_order_repository.find_by_id(order_id)
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada"
            )

        current_status = str(current.get("status", ""))
        if current_status not in {OrderStatusEnum.draft.value, OrderStatusEnum.confirmed.value}:
            raise _build_transition_error(current_status, OrderStatusEnum.cancelled)

        updated = await self.purchase_order_repository.update_status(
            order_id,
            OrderStatusEnum.cancelled,
            "cancelled_at",
        )
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada"
            )
        return _to_order_response(updated)
