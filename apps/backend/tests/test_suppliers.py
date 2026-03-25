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
from purchases.dependencies import get_supplier_service  # noqa: E402
from purchases.routers.suppliers_router import router as suppliers_router  # noqa: E402
from purchases.schemas import SupplierRequest, SupplierResponse, SupplierUpdateRequest  # noqa: E402


class FakeSupplierService:
    def __init__(self) -> None:
        self.suppliers: dict[str, SupplierResponse] = {}

    async def create_supplier(self, payload: SupplierRequest) -> SupplierResponse:
        if payload.ruc and any(supplier.ruc == payload.ruc for supplier in self.suppliers.values()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un proveedor con ese RUC",
            )

        supplier_id = f"sup-{len(self.suppliers) + 1}"
        now = datetime.now(UTC)
        supplier = SupplierResponse(
            id=supplier_id,
            name=payload.name,
            ruc=payload.ruc,
            contact_name=payload.contact_name,
            contact_email=payload.contact_email,
            contact_phone=payload.contact_phone,
            address=payload.address,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.suppliers[supplier_id] = supplier
        return supplier

    async def list_suppliers(self) -> list[SupplierResponse]:
        return list(self.suppliers.values())

    async def get_supplier(self, supplier_id: str) -> SupplierResponse:
        supplier = self.suppliers.get(supplier_id)
        if supplier is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proveedor no encontrado",
            )
        return supplier

    async def update_supplier(
        self,
        supplier_id: str,
        payload: SupplierUpdateRequest,
    ) -> SupplierResponse:
        current = self.suppliers.get(supplier_id)
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proveedor no encontrado",
            )

        updates = payload.model_dump(exclude_none=True)
        updated = current.model_copy(
            update={
                **updates,
                "updated_at": datetime.now(UTC),
            }
        )
        self.suppliers[supplier_id] = updated
        return updated


def _build_user(role: RoleEnum) -> UserResponse:
    return UserResponse(
        id=f"{role.value}-1",
        email=f"{role.value}@nexus.example.com",
        full_name=f"{role.value.title()} User",
        role=role,
        is_active=True,
        created_at=datetime.now(UTC),
    )


def _build_app(service: FakeSupplierService, user: UserResponse) -> FastAPI:
    app = FastAPI()
    app.include_router(suppliers_router, prefix="/suppliers")
    app.dependency_overrides[get_supplier_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: user
    return app


@pytest.mark.asyncio
async def test_should_create_supplier_and_return_201_when_data_is_valid() -> None:
    service = FakeSupplierService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/suppliers",
            json={
                "name": "Proveedor Uno",
                "ruc": "1790012345001",
                "contact_name": "Ana Torres",
                "contact_email": "ana@proveedor.com",
                "contact_phone": "0991111111",
                "address": "Av. Siempre Viva 123",
            },
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Proveedor Uno"


@pytest.mark.asyncio
async def test_should_return_409_when_ruc_already_exists() -> None:
    service = FakeSupplierService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        first = await client.post(
            "/suppliers",
            json={
                "name": "Proveedor Uno",
                "ruc": "1790012345001",
                "contact_name": "Ana Torres",
                "contact_email": "ana@proveedor.com",
            },
        )
        second = await client.post(
            "/suppliers",
            json={
                "name": "Proveedor Dos",
                "ruc": "1790012345001",
                "contact_name": "Luis Ruiz",
                "contact_email": "luis@proveedor.com",
            },
        )

    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_should_deactivate_supplier_and_keep_document_in_collection() -> None:
    service = FakeSupplierService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/suppliers",
            json={
                "name": "Proveedor Uno",
                "ruc": "1790012345001",
                "contact_name": "Ana Torres",
                "contact_email": "ana@proveedor.com",
            },
        )
        supplier_id = created.json()["id"]
        response = await client.patch(
            f"/suppliers/{supplier_id}",
            json={"is_active": False},
        )

    assert response.status_code == 200
    assert supplier_id in service.suppliers
    assert service.suppliers[supplier_id].is_active is False


@pytest.mark.asyncio
async def test_should_return_403_when_vendedor_tries_to_access_suppliers() -> None:
    service = FakeSupplierService()
    app = _build_app(service, _build_user(RoleEnum.vendedor))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/suppliers")

    assert response.status_code == 403
