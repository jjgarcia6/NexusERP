from __future__ import annotations

from typing import Protocol

from inventory.services.inventory_service import InventoryService
from purchases.schemas import PurchaseOrderResponse


class InventoryServiceProtocol(Protocol):
    async def register_stock_entries(self, order: PurchaseOrderResponse) -> None: ...


class PurchaseOrderInventoryAdapter:
    def __init__(self, inventory_service: InventoryService) -> None:
        self.inventory_service = inventory_service

    async def register_stock_entries(self, order: PurchaseOrderResponse) -> None:
        await self.inventory_service.register_stock_entries(order.id, order.lines)
