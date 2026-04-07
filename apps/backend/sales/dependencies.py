from __future__ import annotations

from catalog.repositories.product_repository import ProductRepository
from core.database import get_database
from core.settings import get_settings
from customers.repositories.customer_repository import CustomerRepository
from inventory.repositories.stock_level_repository import StockLevelRepository
from inventory.repositories.stock_movement_repository import StockMovementRepository
from inventory.services.inventory_service import InventoryService
from sales.repositories.invoice_sequence_repository import InvoiceSequenceRepository
from sales.repositories.sale_repository import SaleRepository
from sales.services.sale_service import SaleService


def get_sale_service() -> SaleService:
    database = get_database()
    sale_repository = SaleRepository(database)
    customer_repository = CustomerRepository(database)
    product_repository = ProductRepository(database)
    invoice_sequence_repository = InvoiceSequenceRepository(database)
    stock_level_repository = StockLevelRepository(database)
    stock_movement_repository = StockMovementRepository(database)
    inventory_service = InventoryService(
        product_repository=product_repository,
        stock_level_repository=stock_level_repository,
        stock_movement_repository=stock_movement_repository,
    )
    return SaleService(
        sale_repository=sale_repository,
        customer_repository=customer_repository,
        product_repository=product_repository,
        invoice_sequence_repository=invoice_sequence_repository,
        inventory_service=inventory_service,
    )


def get_point_of_sale() -> str:
    settings = get_settings()
    return settings.pos_point_of_sale
