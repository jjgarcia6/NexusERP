from __future__ import annotations

from catalog.repositories.product_repository import ProductRepository
from core.database import get_database
from inventory.repositories.stock_level_repository import StockLevelRepository
from inventory.repositories.stock_movement_repository import StockMovementRepository
from inventory.services.inventory_service import InventoryService
from purchases.repositories.purchase_order_repository import PurchaseOrderRepository
from purchases.repositories.supplier_repository import SupplierRepository
from purchases.services.inventory_stub_service import PurchaseOrderInventoryAdapter
from purchases.services.purchase_order_service import PurchaseOrderService
from purchases.services.supplier_service import SupplierService


def get_supplier_service() -> SupplierService:
    database = get_database()
    supplier_repository = SupplierRepository(database)
    return SupplierService(supplier_repository)


def get_purchase_order_service() -> PurchaseOrderService:
    database = get_database()
    purchase_order_repository = PurchaseOrderRepository(database)
    supplier_repository = SupplierRepository(database)
    product_repository = ProductRepository(database)
    stock_level_repository = StockLevelRepository(database)
    stock_movement_repository = StockMovementRepository(database)
    inventory_service = InventoryService(
        product_repository=product_repository,
        stock_level_repository=stock_level_repository,
        stock_movement_repository=stock_movement_repository,
    )
    inventory_adapter = PurchaseOrderInventoryAdapter(inventory_service)
    return PurchaseOrderService(
        purchase_order_repository=purchase_order_repository,
        supplier_repository=supplier_repository,
        product_repository=product_repository,
        inventory_service=inventory_adapter,
    )
