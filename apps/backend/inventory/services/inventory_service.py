from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, status

from catalog.repositories.product_repository import ProductRepository
from inventory.repositories.stock_level_repository import StockLevelRepository
from inventory.repositories.stock_movement_repository import StockMovementRepository
from inventory.schemas import MovementTypeEnum, StockMovementRequest
from inventory.service_protocol import InventoryServiceProtocol
from purchases.schemas import PurchaseOrderLineResponse

logger = logging.getLogger(__name__)


class InventoryService(InventoryServiceProtocol):
    def __init__(
        self,
        product_repository: ProductRepository,
        stock_level_repository: StockLevelRepository,
        stock_movement_repository: StockMovementRepository,
    ) -> None:
        self.product_repository = product_repository
        self.stock_level_repository = stock_level_repository
        self.stock_movement_repository = stock_movement_repository

    async def initialize_stock(
        self,
        product_id: str,
        quantity: int,
        min_stock: int,
        user_id: str,
    ) -> dict[str, Any]:
        product = await self.product_repository.find_by_id(product_id, is_active=True)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado o inactivo",
            )

        level = await self.stock_level_repository.find_by_product_id(product_id)
        if level is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El producto ya tiene stock inicializado. "
                    "Use un movimiento de ajuste para modificarlo"
                ),
            )

        created_level = await self.stock_level_repository.create_level(
            product_id=product_id,
            product_name=str(product.get("name") or ""),
            quantity=quantity,
            min_stock=min_stock,
        )

        await self.stock_movement_repository.create_movement(
            {
                "product_id": created_level["product_id"],
                "product_name": created_level["product_name"],
                "type": MovementTypeEnum.manual_entry.value,
                "quantity": quantity,
                "quantity_before": 0,
                "quantity_after": quantity,
                "reason": "Inicialización de stock",
                "reference_id": None,
                "reference_type": None,
                "created_by": user_id,
            }
        )

        return self._serialize_stock_level(created_level)

    async def register_movement(
        self,
        request: StockMovementRequest,
        user_id: str,
    ) -> dict[str, Any]:
        level = await self.stock_level_repository.find_by_product_id(request.product_id)
        if level is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El producto no tiene stock inicializado",
            )

        quantity_before = int(level.get("available_quantity", 0))
        min_stock = int(level.get("min_stock", 0))
        delta = int(request.quantity)

        if request.type == MovementTypeEnum.manual_exit:
            delta = -abs(delta)
        elif request.type == MovementTypeEnum.manual_entry:
            delta = abs(delta)

        requested_quantity = abs(delta)
        if delta < 0 and quantity_before < requested_quantity:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Stock insuficiente. "
                    f"Disponible: {quantity_before}, solicitado: {requested_quantity}"
                ),
            )

        updated_level = await self.stock_level_repository.increment_quantity(
            request.product_id,
            delta,
            min_stock,
        )
        if updated_level is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El producto no tiene stock inicializado",
            )

        quantity_after = int(updated_level.get("available_quantity", quantity_before + delta))
        try:
            movement = await self.stock_movement_repository.create_movement(
                {
                    "product_id": updated_level["product_id"],
                    "product_name": updated_level.get("product_name", ""),
                    "type": request.type.value,
                    "quantity": request.quantity,
                    "quantity_before": quantity_before,
                    "quantity_after": quantity_after,
                    "reason": request.reason,
                    "reference_id": None,
                    "reference_type": None,
                    "created_by": user_id,
                }
            )
        except Exception as exc:
            await self.stock_level_repository.increment_quantity(
                request.product_id,
                -delta,
                min_stock,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo registrar el movimiento de inventario",
            ) from exc

        return self._serialize_movement(movement)

    async def register_stock_entries(
        self,
        order_id: str,
        lines: list[PurchaseOrderLineResponse],
    ) -> None:
        applied: list[tuple[str, int, int]] = []

        try:
            for line in lines:
                product = await self.product_repository.find_by_id(line.product_id, is_active=True)
                if product is None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Producto invalido en orden de compra: {line.product_id}",
                    )

                level = await self.stock_level_repository.find_by_product_id(line.product_id)
                if level is None:
                    level = await self.stock_level_repository.create_level(
                        product_id=line.product_id,
                        product_name=str(product.get("name") or line.product_name),
                        quantity=0,
                        min_stock=int(product.get("min_stock", 0) or 0),
                    )

                min_stock = int(level.get("min_stock", 0))
                quantity_before = int(level.get("available_quantity", 0))
                updated_level = await self.stock_level_repository.increment_quantity(
                    line.product_id,
                    int(line.quantity),
                    min_stock,
                )
                if updated_level is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No se pudo actualizar el nivel de stock para {line.product_id}",
                    )

                quantity_after = int(
                    updated_level.get("available_quantity", quantity_before + line.quantity)
                )
                applied.append((line.product_id, int(line.quantity), min_stock))
                await self.stock_movement_repository.create_movement(
                    {
                        "product_id": updated_level["product_id"],
                        "product_name": updated_level.get("product_name", line.product_name),
                        "type": MovementTypeEnum.purchase_entry.value,
                        "quantity": int(line.quantity),
                        "quantity_before": quantity_before,
                        "quantity_after": quantity_after,
                        "reason": "Recepción de orden de compra",
                        "reference_id": order_id,
                        "reference_type": "purchase_order",
                        "created_by": "system",
                    }
                )
        except Exception:
            for product_id, quantity, min_stock in reversed(applied):
                await self.stock_level_repository.increment_quantity(
                    product_id,
                    -quantity,
                    min_stock,
                )
            raise

    async def register_sale_exits(
        self,
        sale_id: str,
        lines: list[Any],
    ) -> None:
        # 1. Verificar stock suficiente para todas las líneas
        insufficient = []
        for line in lines:
            product_id = line["product_id"]
            quantity = int(line["quantity"])
            level = await self.stock_level_repository.find_by_product_id(product_id)
            available = int(level.get("available_quantity", 0)) if level else 0
            if available < quantity:
                insufficient.append(
                    {"product_id": product_id, "available": available, "requested": quantity}
                )
        if insufficient:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "Stock insuficiente en uno o más productos",
                    "products": insufficient,
                },
            )

        # 2. Decrementar stock y registrar movimientos
        decremented = []
        try:
            for line in lines:
                product_id = line["product_id"]
                quantity = int(line["quantity"])
                level = await self.stock_level_repository.find_by_product_id(product_id)
                min_stock = int(level.get("min_stock", 0)) if level else 0
                # Decrementar stock
                updated_level = await self.stock_level_repository.increment_quantity(
                    product_id,
                    -quantity,
                    min_stock,
                )
                if updated_level is None:
                    raise Exception(f"No se pudo decrementar stock para {product_id}")
                decremented.append((product_id, quantity, min_stock))
                quantity_before = int(updated_level.get("available_quantity", 0)) + quantity
                quantity_after = int(
                    updated_level.get("available_quantity", quantity_before - quantity)
                )
                # Registrar movimiento
                await self.stock_movement_repository.create_movement(
                    {
                        "product_id": product_id,
                        "product_name": line.get("product_name", ""),
                        "type": MovementTypeEnum.sale_exit.value,
                        "quantity": quantity,
                        "quantity_before": quantity_before,
                        "quantity_after": quantity_after,
                        "reason": "Venta confirmada",
                        "reference_id": sale_id,
                        "reference_type": "sale",
                        "created_by": line.get("created_by"),
                    }
                )
        except Exception as e:
            # Compensación: revertir decrementos en orden inverso
            for product_id, quantity, min_stock in reversed(decremented):
                await self.stock_level_repository.increment_quantity(
                    product_id,
                    quantity,
                    min_stock,
                )
                # Registrar movimiento de compensación (opcional)
                await self.stock_movement_repository.create_movement(
                    {
                        "product_id": product_id,
                        "product_name": "",
                        "type": MovementTypeEnum.manual_entry.value,
                        "quantity": quantity,
                        "quantity_before": 0,
                        "quantity_after": 0,
                        "reason": "Compensación por error en venta",
                        "reference_id": sale_id,
                        "reference_type": "sale_compensate",
                        "created_by": None,
                    }
                )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error al decrementar stock: {str(e)}",
            ) from e

    async def revert_sale_exits(
        self,
        sale_id: str,
        lines: list[Any],
        reason: str,
        reference_type: str,
    ) -> None:
        restored: list[tuple[str, int, int]] = []
        try:
            for line in lines:
                product_id = str(line["product_id"])
                quantity = int(line["quantity"])
                level = await self.stock_level_repository.find_by_product_id(product_id)
                if level is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Nivel de stock no encontrado para {product_id}",
                    )

                min_stock = int(level.get("min_stock", 0))
                quantity_before = int(level.get("available_quantity", 0))
                updated_level = await self.stock_level_repository.increment_quantity(
                    product_id,
                    quantity,
                    min_stock,
                )
                if updated_level is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No se pudo revertir stock para {product_id}",
                    )

                quantity_after = int(
                    updated_level.get("available_quantity", quantity_before + quantity)
                )
                restored.append((product_id, quantity, min_stock))

                await self.stock_movement_repository.create_movement(
                    {
                        "product_id": product_id,
                        "product_name": line.get("product_name", ""),
                        "type": MovementTypeEnum.manual_entry.value,
                        "quantity": quantity,
                        "quantity_before": quantity_before,
                        "quantity_after": quantity_after,
                        "reason": reason,
                        "reference_id": sale_id,
                        "reference_type": reference_type,
                        "created_by": line.get("created_by"),
                    }
                )
        except Exception as exc:
            for product_id, quantity, min_stock in reversed(restored):
                await self.stock_level_repository.increment_quantity(
                    product_id,
                    -quantity,
                    min_stock,
                )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo revertir stock de la venta",
            ) from exc

    async def check_stock_availability(
        self,
        product_id: str,
        quantity: int,
    ) -> bool:
        level = await self.stock_level_repository.find_by_product_id(product_id)
        if level is None:
            return False
        available = int(level.get("available_quantity", 0))
        return available >= quantity

    async def list_stock_levels(
        self,
        *,
        low_stock: bool | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        levels, total = await self.stock_level_repository.find_all(
            low_stock=low_stock,
            skip=skip,
            limit=limit,
        )
        return [self._serialize_stock_level(item) for item in levels], total

    async def get_stock_level(self, product_id: str) -> dict[str, Any]:
        product = await self.product_repository.find_by_id(product_id, is_active=True)
        level = await self.stock_level_repository.find_by_product_id(product_id)
        if product is None or level is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado o sin stock inicializado",
            )
        return self._serialize_stock_level(level)

    async def list_movements(
        self,
        *,
        product_id: str | None,
        movement_type: str | None,
        from_date: Any,
        to_date: Any,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        movements, total = await self.stock_movement_repository.find_all(
            product_id=product_id,
            movement_type=movement_type,
            from_date=from_date,
            to_date=to_date,
            skip=skip,
            limit=limit,
        )
        return [self._serialize_movement(item) for item in movements], total

    def _serialize_stock_level(self, level: dict[str, Any]) -> dict[str, Any]:
        return {
            "product_id": str(level.get("product_id")),
            "product_name": str(level.get("product_name") or ""),
            "available_quantity": int(level.get("available_quantity", 0)),
            "min_stock": int(level.get("min_stock", 0)),
            "low_stock": bool(level.get("low_stock", False)),
            "updated_at": level.get("updated_at"),
        }

    def _serialize_movement(self, movement: dict[str, Any]) -> dict[str, Any]:
        reference = movement.get("reference_id")
        return {
            "id": str(movement.get("_id")),
            "product_id": str(movement.get("product_id")),
            "product_name": str(movement.get("product_name") or ""),
            "type": movement.get("type"),
            "quantity": int(movement.get("quantity", 0)),
            "quantity_before": int(movement.get("quantity_before", 0)),
            "quantity_after": int(movement.get("quantity_after", 0)),
            "reason": movement.get("reason"),
            "reference_id": (str(reference) if reference is not None else None),
            "reference_type": movement.get("reference_type"),
            "created_at": movement.get("created_at"),
        }
