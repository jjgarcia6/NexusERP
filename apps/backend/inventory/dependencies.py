from __future__ import annotations

from catalog.repositories.product_repository import ProductRepository
from core.database import get_database
from inventory.repositories.stock_level_repository import StockLevelRepository
from inventory.repositories.stock_movement_repository import StockMovementRepository
from inventory.services.inventory_service import InventoryService


def get_inventory_service() -> InventoryService:
    database = get_database()
    product_repository = ProductRepository(database)
    stock_level_repository = StockLevelRepository(database)
    stock_movement_repository = StockMovementRepository(database)
    return InventoryService(
        product_repository=product_repository,
        stock_level_repository=stock_level_repository,
        stock_movement_repository=stock_movement_repository,
    )
