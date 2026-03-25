from __future__ import annotations

from catalog.repositories.product_repository import ProductRepository
from core.database import get_database
from purchases.repositories.purchase_order_repository import PurchaseOrderRepository
from purchases.repositories.supplier_repository import SupplierRepository
from purchases.services.inventory_stub_service import InventoryStubService
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
    inventory_service = InventoryStubService()
    return PurchaseOrderService(
        purchase_order_repository=purchase_order_repository,
        supplier_repository=supplier_repository,
        product_repository=product_repository,
        inventory_service=inventory_service,
    )
