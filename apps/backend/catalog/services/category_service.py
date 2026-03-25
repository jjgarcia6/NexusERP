from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from catalog.repositories.category_repository import CategoryRepository
from catalog.schemas import CategoryRequest, CategoryResponse, CategoryUpdateRequest


def _to_category_response(document: dict[str, object]) -> CategoryResponse:
    created_at = document.get("created_at")
    updated_at = document.get("updated_at")
    if not isinstance(created_at, datetime) or not isinstance(updated_at, datetime):
        raise TypeError("Invalid category date fields")

    return CategoryResponse(
        id=str(document["_id"]),
        name=str(document["name"]),
        description=(str(document["description"]) if document.get("description") else None),
        is_active=bool(document["is_active"]),
        created_at=created_at,
        updated_at=updated_at,
    )


class CategoryService:
    def __init__(self, category_repository: CategoryRepository) -> None:
        self.category_repository = category_repository

    async def create_category(self, payload: CategoryRequest) -> CategoryResponse:
        existing = await self.category_repository.find_by_name(payload.name)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría con ese nombre",
            )

        try:
            category = await self.category_repository.create_category(
                name=payload.name,
                description=payload.description,
            )
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría con ese nombre",
            ) from exc

        return _to_category_response(category)

    async def list_categories(self) -> list[CategoryResponse]:
        categories = await self.category_repository.find_all()
        return [_to_category_response(category) for category in categories]

    async def get_category(self, category_id: str) -> CategoryResponse:
        category = await self.category_repository.find_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
        return _to_category_response(category)

    async def update_category(
        self,
        category_id: str,
        payload: CategoryUpdateRequest,
    ) -> CategoryResponse:
        current = await self.category_repository.find_by_id(category_id)
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )

        updates = payload.model_dump(exclude_none=True)
        if "name" in updates:
            next_name = str(updates["name"])
            if next_name != current["name"]:
                existing = await self.category_repository.find_by_name(next_name)
                if existing is not None and str(existing["_id"]) != category_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Ya existe una categoría con ese nombre",
                    )

        if not updates:
            return _to_category_response(current)

        updated = await self.category_repository.update_category(category_id, updates)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
        return _to_category_response(updated)

    async def delete_category(self, category_id: str) -> None:
        category = await self.category_repository.find_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )

        has_products = await self.category_repository.has_active_products(category_id)
        if has_products:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar una categoría con productos activos asociados",
            )

        deleted = await self.category_repository.delete_category(category_id)
        if deleted == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
