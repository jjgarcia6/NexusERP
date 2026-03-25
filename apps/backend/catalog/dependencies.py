from __future__ import annotations

from catalog.repositories.category_repository import CategoryRepository
from catalog.repositories.product_repository import ProductRepository
from catalog.services.category_service import CategoryService
from catalog.services.product_service import ProductService
from core.database import get_database
from inventory.repositories.stock_level_repository import StockLevelRepository


def get_category_service() -> CategoryService:
    database = get_database()
    category_repository = CategoryRepository(database)
    return CategoryService(category_repository)


def get_product_service() -> ProductService:
    database = get_database()
    category_repository = CategoryRepository(database)
    product_repository = ProductRepository(database)
    stock_level_repository = StockLevelRepository(database)
    return ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
        stock_level_repository=stock_level_repository,
    )
