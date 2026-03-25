from __future__ import annotations

import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException, status
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth.dependencies import get_current_user  # noqa: E402
from auth.schemas import RoleEnum, UserResponse  # noqa: E402
from catalog.dependencies import get_product_service  # noqa: E402
from catalog.routers.products_router import router as products_router  # noqa: E402
from catalog.schemas import ProductRequest, ProductUpdateRequest  # noqa: E402


class FakeProductService:
    def __init__(self) -> None:
        self.categories = {
            "cat-1": "Bebidas",
            "cat-2": "Snacks",
        }
        self.products: dict[str, dict[str, object]] = {}

    async def create_product(
        self,
        payload: ProductRequest,
        *,
        created_by: str,
    ) -> dict[str, object]:
        if payload.category_id not in self.categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría especificada no existe",
            )

        product_id = f"prd-{len(self.products) + 1}"
        now = datetime.now(UTC)
        document: dict[str, object] = {
            "id": product_id,
            "name": payload.name,
            "description": payload.description,
            "sku": payload.sku,
            "price": payload.price,
            "cost": payload.cost,
            "category_id": payload.category_id,
            "category_name": self.categories[payload.category_id],
            "image_url": payload.image_url,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "created_by": created_by,
        }
        self.products[product_id] = document
        return document

    async def list_products(
        self,
        *,
        search: str | None,
        category_id: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, object]], int]:
        products = [
            product
            for product in self.products.values()
            if bool(product["is_active"])
        ]

        if search:
            lower = search.lower()
            products = [
                product
                for product in products
                if lower in str(product["name"]).lower()
            ]

        if category_id:
            products = [
                product
                for product in products
                if str(product["category_id"]) == category_id
            ]

        total = len(products)
        page = products[skip : skip + limit]
        return page, total

    async def get_product(self, product_id: str) -> dict[str, object]:
        product = self.products.get(product_id)
        if product is None or not bool(product["is_active"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )
        return product

    async def update_product(
        self,
        product_id: str,
        payload: ProductUpdateRequest,
    ) -> dict[str, object]:
        product = self.products.get(product_id)
        if product is None or not bool(product["is_active"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )

        updates = payload.model_dump(exclude_none=True)
        if "category_id" in updates:
            next_category = str(updates["category_id"])
            if next_category not in self.categories:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La categoría especificada no existe",
                )
            updates["category_name"] = self.categories[next_category]

        product.update(updates)
        product["updated_at"] = datetime.now(UTC)
        return product


def _build_user(role: RoleEnum) -> UserResponse:
    return UserResponse(
        id=f"{role.value}-1",
        email=f"{role.value}@nexus.example.com",
        full_name=f"{role.value.title()} User",
        role=role,
        is_active=True,
        created_at=datetime.now(UTC),
    )


def _build_app(service: FakeProductService, user: UserResponse) -> FastAPI:
    app = FastAPI()
    app.include_router(products_router, prefix="/products")
    app.dependency_overrides[get_product_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: user
    return app


async def _create_product(
    client: AsyncClient,
    *,
    name: str,
    category_id: str = "cat-1",
) -> dict[str, object]:
    response = await client.post(
        "/products",
        json={
            "name": name,
                "description": "Descripcion",
            "sku": f"SKU-{name}",
                "price": "10.50",
                "cost": "5.25",
            "category_id": category_id,
            "image_url": "https://example.com/image.jpg",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_should_create_product_and_return_201_when_data_is_valid() -> None:
    service = FakeProductService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/products",
            json={
                "name": "Agua",
                "description": "Botella",
                "sku": "SKU-AGUA",
                "price": "8.50",
                "cost": "4.25",
                "category_id": "cat-1",
                "image_url": "https://example.com/agua.jpg",
            },
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Agua"


@pytest.mark.asyncio
async def test_should_return_404_when_category_id_does_not_exist() -> None:
    service = FakeProductService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/products",
            json={
                "name": "Agua",
                "description": "Botella",
                "sku": "SKU-AGUA",
                "price": "8.50",
                "cost": "4.25",
                "category_id": "missing-cat",
                "image_url": "https://example.com/agua.jpg",
            },
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_should_return_200_with_empty_list_when_search_has_no_results() -> None:
    service = FakeProductService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _create_product(client, name="Agua")
        response = await client.get("/products", params={"search": "NoExiste"})

    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.asyncio
async def test_should_filter_products_by_category_id() -> None:
    service = FakeProductService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _create_product(client, name="Agua", category_id="cat-1")
        await _create_product(client, name="Papas", category_id="cat-2")
        response = await client.get("/products", params={"category_id": "cat-1"})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["category_id"] == "cat-1"


@pytest.mark.asyncio
async def test_should_paginate_products_correctly() -> None:
    service = FakeProductService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await _create_product(client, name="Agua")
        await _create_product(client, name="Papas")
        await _create_product(client, name="Jugo")
        response = await client.get("/products", params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["total"] == 3


@pytest.mark.asyncio
async def test_should_deactivate_product_and_keep_document_in_collection() -> None:
    service = FakeProductService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await _create_product(client, name="Agua")
        product_id = str(created["id"])
        update = await client.patch(f"/products/{product_id}", json={"is_active": False})
        listed = await client.get("/products")

    assert update.status_code == 200
    assert len(listed.json()["items"]) == 0
    assert product_id in service.products
    assert service.products[product_id]["is_active"] is False


@pytest.mark.asyncio
async def test_should_hide_cost_field_when_role_is_vendedor() -> None:
    service = FakeProductService()
    admin_app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(
        transport=ASGITransport(app=admin_app),
        base_url="http://test",
    ) as client:
        created = await _create_product(client, name="Agua")
        product_id = str(created["id"])

    seller_app = _build_app(service, _build_user(RoleEnum.vendedor))
    async with AsyncClient(
        transport=ASGITransport(app=seller_app),
        base_url="http://test",
    ) as client:
        response = await client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["cost"] is None


@pytest.mark.asyncio
async def test_should_show_cost_field_when_role_is_admin() -> None:
    service = FakeProductService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await _create_product(client, name="Agua")
        product_id = str(created["id"])
        response = await client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert Decimal(str(response.json()["cost"])) > Decimal("0")


@pytest.mark.asyncio
async def test_should_return_403_when_bodeguero_tries_to_create_product() -> None:
    service = FakeProductService()
    app = _build_app(service, _build_user(RoleEnum.bodeguero))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/products",
            json={
                "name": "Agua",
                "description": "Botella",
                "sku": "SKU-AGUA",
                "price": "8.50",
                "cost": "4.25",
                "category_id": "cat-1",
                "image_url": "https://example.com/agua.jpg",
            },
        )

    assert response.status_code == 403
