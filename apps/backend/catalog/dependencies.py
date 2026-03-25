from __future__ import annotations

from catalog.repositories.category_repository import CategoryRepository
from catalog.repositories.product_repository import ProductRepository
from catalog.services.category_service import CategoryService
from catalog.services.product_service import ProductService
from core.database import get_database


def get_category_service() -> CategoryService:
    database = get_database()
    category_repository = CategoryRepository(database)
    return CategoryService(category_repository)


def get_product_service() -> ProductService:
    database = get_database()
    category_repository = CategoryRepository(database)
    product_repository = ProductRepository(database)
    return ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )
