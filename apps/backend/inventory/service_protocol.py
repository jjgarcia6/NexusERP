from __future__ import annotations

from typing import Any, Protocol

from purchases.schemas import PurchaseOrderLineResponse


class InventoryServiceProtocol(Protocol):
    async def register_stock_entries(
        self,
        order_id: str,
        lines: list[PurchaseOrderLineResponse],
    ) -> None: ...

    async def register_sale_exits(
        self,
        sale_id: str,
        lines: list[Any],
    ) -> None: ...

    async def check_stock_availability(
        self,
        product_id: str,
        quantity: int,
    ) -> bool: ...
