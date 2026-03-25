from __future__ import annotations

from typing import Protocol

from purchases.schemas import PurchaseOrderResponse


class InventoryServiceProtocol(Protocol):
    async def register_stock_entries(self, order: PurchaseOrderResponse) -> None: ...


class InventoryStubService:
    async def register_stock_entries(self, order: PurchaseOrderResponse) -> None:
        _ = order
