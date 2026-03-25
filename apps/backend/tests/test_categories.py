from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException, status
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth.dependencies import get_current_user  # noqa: E402
from auth.schemas import RoleEnum, UserResponse  # noqa: E402
from catalog.dependencies import get_category_service  # noqa: E402
from catalog.routers.categories_router import router as categories_router  # noqa: E402
from catalog.schemas import CategoryRequest, CategoryResponse, CategoryUpdateRequest  # noqa: E402


class FakeCategoryService:
    def __init__(self) -> None:
        self.categories: dict[str, CategoryResponse] = {}
        self.active_products_by_category: dict[str, int] = {}

    async def create_category(self, payload: CategoryRequest) -> CategoryResponse:
        if any(category.name == payload.name for category in self.categories.values()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría con ese nombre",
            )

        category_id = f"cat-{len(self.categories) + 1}"
        now = datetime.now(UTC)
        category = CategoryResponse(
            id=category_id,
            name=payload.name,
            description=payload.description,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.categories[category_id] = category
        return category

    async def list_categories(self) -> list[CategoryResponse]:
        return list(self.categories.values())

    async def get_category(self, category_id: str) -> CategoryResponse:
        category = self.categories.get(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
        return category

    async def update_category(
        self,
        category_id: str,
        payload: CategoryUpdateRequest,
    ) -> CategoryResponse:
        category = self.categories.get(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )

        updates = payload.model_dump(exclude_none=True)
        next_name = updates.get("name")
        if next_name is not None and any(
            current.id != category_id and current.name == next_name
            for current in self.categories.values()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría con ese nombre",
            )

        updated = category.model_copy(
            update={
                **updates,
                "updated_at": datetime.now(UTC),
            }
        )
        self.categories[category_id] = updated
        return updated

    async def delete_category(self, category_id: str) -> None:
        category = self.categories.get(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )

        if self.active_products_by_category.get(category_id, 0) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar una categoría con productos activos asociados",
            )

        del self.categories[category_id]


def _build_user(role: RoleEnum) -> UserResponse:
    return UserResponse(
        id=f"{role.value}-1",
        email=f"{role.value}@nexus.example.com",
        full_name=f"{role.value.title()} User",
        role=role,
        is_active=True,
        created_at=datetime.now(UTC),
    )


def _build_app(service: FakeCategoryService, user: UserResponse) -> FastAPI:
    app = FastAPI()
    app.include_router(categories_router, prefix="/categories")
    app.dependency_overrides[get_category_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: user
    return app


@pytest.mark.asyncio
async def test_should_create_category_and_return_201_when_data_is_valid() -> None:
    service = FakeCategoryService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/categories",
            json={"name": "Bebidas", "description": "Líquidos"},
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Bebidas"


@pytest.mark.asyncio
async def test_should_return_409_when_category_name_already_exists() -> None:
    service = FakeCategoryService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post(
            "/categories",
            json={"name": "Bebidas", "description": "Líquidos"},
        )
        second = await client.post(
            "/categories",
            json={"name": "Bebidas", "description": "Duplicada"},
        )

    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_should_update_category_and_return_200_when_admin() -> None:
    service = FakeCategoryService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/categories",
            json={"name": "Bebidas", "description": "Líquidos"},
        )
        category_id = created.json()["id"]
        updated = await client.patch(
            f"/categories/{category_id}",
            json={"name": "Bebidas frías"},
        )

    assert updated.status_code == 200
    assert updated.json()["name"] == "Bebidas frías"


@pytest.mark.asyncio
async def test_should_return_409_when_deleting_category_with_active_products() -> None:
    service = FakeCategoryService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/categories",
            json={"name": "Bebidas", "description": "Líquidos"},
        )
        category_id = created.json()["id"]
        service.active_products_by_category[category_id] = 1
        deleted = await client.delete(f"/categories/{category_id}")

    assert deleted.status_code == 409


@pytest.mark.asyncio
async def test_should_delete_category_and_return_200_when_no_active_products() -> None:
    service = FakeCategoryService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/categories",
            json={"name": "Bebidas", "description": "Líquidos"},
        )
        category_id = created.json()["id"]
        deleted = await client.delete(f"/categories/{category_id}")

    assert deleted.status_code == 200
    assert deleted.json() == {"message": "ok"}


@pytest.mark.asyncio
async def test_should_return_403_when_vendedor_tries_to_create_category() -> None:
    service = FakeCategoryService()
    app = _build_app(service, _build_user(RoleEnum.vendedor))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/categories",
            json={"name": "Bebidas", "description": "Líquidos"},
        )

    assert response.status_code == 403
