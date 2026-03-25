from __future__ import annotations

from decimal import Decimal
from typing import Any

from bson import ObjectId
from bson.decimal128 import Decimal128
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from catalog.repositories.category_repository import CategoryRepository
from catalog.repositories.product_repository import ProductRepository
from catalog.schemas import ProductRequest, ProductUpdateRequest
from inventory.repositories.stock_level_repository import StockLevelRepository


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


def _to_bson_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return Decimal128(value)
    return value


def _to_bson_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: _to_bson_value(value) for key, value in payload.items()}


def _to_product_dict(document: dict[str, Any]) -> dict[str, Any]:
    product: dict[str, Any] = {
        "id": str(document["_id"]),
        "name": str(document["name"]),
        "description": (str(document["description"]) if document.get("description") else None),
        "sku": (str(document["sku"]) if document.get("sku") else None),
        "price": _to_decimal(document.get("price")) or Decimal("0"),
        "cost": _to_decimal(document.get("cost")),
        "category_id": str(document["category_id"]),
        "category_name": str(document.get("category_name") or ""),
        "image_url": (str(document["image_url"]) if document.get("image_url") else None),
        "is_active": bool(document["is_active"]),
        "created_at": document["created_at"],
        "updated_at": document["updated_at"],
    }
    return product


class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
        stock_level_repository: StockLevelRepository,
    ) -> None:
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.stock_level_repository = stock_level_repository

    async def create_product(self, payload: ProductRequest, *, created_by: str) -> dict[str, Any]:
        category = await self.category_repository.find_by_id(payload.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría especificada no existe",
            )

        if payload.sku:
            sku_in_use = await self.product_repository.find_by_sku(payload.sku)
            if sku_in_use is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un producto con ese SKU",
                )

        to_insert = _to_bson_payload(payload.model_dump())
        to_insert["category_id"] = ObjectId(payload.category_id)
        to_insert["created_by"] = ObjectId(created_by)

        try:
            created = await self.product_repository.create_product(to_insert)
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un producto con ese SKU",
            ) from exc

        created["category_name"] = str(category["name"])
        return _to_product_dict(created)

    async def list_products(
        self,
        *,
        search: str | None,
        category_id: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        items, total = await self.product_repository.find_all(
            search=search,
            category_id=category_id,
            skip=skip,
            limit=limit,
            is_active=True,
        )
        product_items = [_to_product_dict(item) for item in items]
        return product_items, total

    async def get_product(self, product_id: str) -> dict[str, Any]:
        product = await self.product_repository.find_by_id(product_id, is_active=True)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )
        return _to_product_dict(product)

    async def update_product(
        self,
        product_id: str,
        payload: ProductUpdateRequest,
    ) -> dict[str, Any]:
        product = await self.product_repository.find_by_id(product_id, is_active=True)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        updates = _to_bson_payload(payload.model_dump(exclude_none=True))
        if not updates:
            return _to_product_dict(product)

        if "category_id" in updates:
            next_category_id = str(updates["category_id"])
            category = await self.category_repository.find_by_id(next_category_id)
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La categoría especificada no existe",
                )
            updates["category_id"] = ObjectId(next_category_id)

        if "sku" in updates and updates["sku"]:
            current_sku = product.get("sku")
            next_sku = str(updates["sku"])
            if current_sku != next_sku:
                sku_in_use = await self.product_repository.find_by_sku(next_sku)
                if sku_in_use is not None and str(sku_in_use["_id"]) != product_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Ya existe un producto con ese SKU",
                    )

        if updates.get("is_active") is False:
            return await self.deactivate_product(product_id, updates)

        try:
            updated = await self.product_repository.update_product(product_id, updates)
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un producto con ese SKU",
            ) from exc

        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        if "min_stock" in updates:
            await self.stock_level_repository.update_min_stock(
                product_id,
                int(updates["min_stock"]),
            )

        return _to_product_dict(updated)

    async def deactivate_product(
        self,
        product_id: str,
        updates: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        deactivate_updates: dict[str, Any] = {"is_active": False}
        if updates:
            deactivate_updates.update(updates)
            deactivate_updates["is_active"] = False

        updated = await self.product_repository.update_product(product_id, deactivate_updates)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )
        return _to_product_dict(updated)
