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
from purchases.dependencies import get_purchase_order_service  # noqa: E402
from purchases.routers.purchases_router import router as purchases_router  # noqa: E402
from purchases.schemas import (  # noqa: E402
    OrderStatusEnum,
    PurchaseOrderLineRequest,
    PurchaseOrderLineResponse,
    PurchaseOrderListResponse,
    PurchaseOrderRequest,
    PurchaseOrderResponse,
)


class FakePurchaseOrderService:
    def __init__(self) -> None:
        self.suppliers = {
            "sup-1": {"name": "Proveedor Activo", "is_active": True},
            "sup-2": {"name": "Proveedor Inactivo", "is_active": False},
        }
        self.products = {
            "prd-1": {"name": "Producto Activo", "is_active": True},
            "prd-2": {"name": "Producto Inactivo", "is_active": False},
        }
        self.orders: dict[str, PurchaseOrderResponse] = {}
        self.fail_receive_for: set[str] = set()

    async def create_order(
        self,
        payload: PurchaseOrderRequest,
        *,
        created_by: str,
    ) -> PurchaseOrderResponse:
        _ = created_by
        supplier = self.suppliers.get(payload.supplier_id)
        if supplier is None or not supplier["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El proveedor especificado no esta activo",
            )

        lines: list[PurchaseOrderLineResponse] = []
        total = Decimal("0")
        for index, line in enumerate(payload.lines, start=1):
            product = self.products.get(line.product_id)
            if product is None or not product["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"La linea {index} contiene un producto inactivo",
                )
            subtotal = Decimal(line.quantity) * Decimal(line.unit_cost)
            total += subtotal
            lines.append(
                PurchaseOrderLineResponse(
                    product_id=line.product_id,
                    quantity=line.quantity,
                    unit_cost=Decimal(line.unit_cost),
                    product_name=str(product["name"]),
                    subtotal=subtotal,
                )
            )

        now = datetime.now(UTC)
        order_id = f"ord-{len(self.orders) + 1}"
        order = PurchaseOrderResponse(
            id=order_id,
            supplier_id=payload.supplier_id,
            supplier_name=str(supplier["name"]),
            status=OrderStatusEnum.draft,
            lines=lines,
            total=total,
            notes=payload.notes,
            confirmed_at=None,
            received_at=None,
            cancelled_at=None,
            created_at=now,
            updated_at=now,
        )
        self.orders[order_id] = order
        return order

    async def list_orders(
        self,
        *,
        order_status: OrderStatusEnum | None,
        supplier_id: str | None,
        skip: int,
        limit: int,
    ) -> PurchaseOrderListResponse:
        items = list(self.orders.values())
        if order_status is not None:
            items = [order for order in items if order.status == order_status]
        if supplier_id is not None:
            items = [order for order in items if order.supplier_id == supplier_id]
        total = len(items)
        page = items[skip : skip + limit]
        return PurchaseOrderListResponse(items=page, total=total, skip=skip, limit=limit)

    async def get_order(self, order_id: str) -> PurchaseOrderResponse:
        order = self.orders.get(order_id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden de compra no encontrada",
            )
        return order

    async def confirm_order(self, order_id: str) -> PurchaseOrderResponse:
        order = await self.get_order(order_id)
        if order.status != OrderStatusEnum.draft:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Transicion de estado invalida: {order.status.value} -> confirmed",
            )

        updated = order.model_copy(
            update={
                "status": OrderStatusEnum.confirmed,
                "confirmed_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        )
        self.orders[order_id] = updated
        return updated

    async def receive_order(self, order_id: str) -> PurchaseOrderResponse:
        order = await self.get_order(order_id)
        if order.status != OrderStatusEnum.confirmed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Transicion de estado invalida: {order.status.value} -> received",
            )

        if order_id in self.fail_receive_for:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo actualizar el inventario. Intente nuevamente",
            )

        updated = order.model_copy(
            update={
                "status": OrderStatusEnum.received,
                "received_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        )
        self.orders[order_id] = updated
        return updated

    async def cancel_order(self, order_id: str) -> PurchaseOrderResponse:
        order = await self.get_order(order_id)
        if order.status not in {OrderStatusEnum.draft, OrderStatusEnum.confirmed}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Transicion de estado invalida: {order.status.value} -> cancelled",
            )

        updated = order.model_copy(
            update={
                "status": OrderStatusEnum.cancelled,
                "cancelled_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        )
        self.orders[order_id] = updated
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


def _build_app(service: FakePurchaseOrderService, user: UserResponse) -> FastAPI:
    app = FastAPI()
    app.include_router(purchases_router, prefix="/purchases")
    app.dependency_overrides[get_purchase_order_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: user
    return app


def _build_order_payload(*, supplier_id: str = "sup-1", product_id: str = "prd-1") -> dict[str, object]:
    return {
        "supplier_id": supplier_id,
        "lines": [
            {
                "product_id": product_id,
                "quantity": 2,
                "unit_cost": 10.5,
            }
        ],
        "notes": "Orden de prueba",
    }


@pytest.mark.asyncio
async def test_should_create_order_and_return_201_when_data_is_valid() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/purchases", json=_build_order_payload())

    assert response.status_code == 201
    assert response.json()["status"] == "draft"


@pytest.mark.asyncio
async def test_should_return_422_when_supplier_is_inactive() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/purchases",
            json=_build_order_payload(supplier_id="sup-2"),
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_should_return_422_when_product_in_line_is_inactive() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/purchases",
            json=_build_order_payload(product_id="prd-2"),
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_should_confirm_order_and_update_status_to_confirmed() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/purchases", json=_build_order_payload())
        order_id = created.json()["id"]
        response = await client.patch(f"/purchases/{order_id}/confirm")

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_should_return_422_when_confirming_already_confirmed_order() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/purchases", json=_build_order_payload())
        order_id = created.json()["id"]
        first = await client.patch(f"/purchases/{order_id}/confirm")
        second = await client.patch(f"/purchases/{order_id}/confirm")

    assert first.status_code == 200
    assert second.status_code == 422


@pytest.mark.asyncio
async def test_should_receive_order_and_update_status_to_received() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/purchases", json=_build_order_payload())
        order_id = created.json()["id"]
        await client.patch(f"/purchases/{order_id}/confirm")
        response = await client.patch(f"/purchases/{order_id}/receive")

    assert response.status_code == 200
    assert response.json()["status"] == "received"


@pytest.mark.asyncio
async def test_should_keep_order_in_confirmed_when_inventory_service_fails() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/purchases", json=_build_order_payload())
        order_id = created.json()["id"]
        await client.patch(f"/purchases/{order_id}/confirm")
        service.fail_receive_for.add(order_id)
        failed = await client.patch(f"/purchases/{order_id}/receive")
        detail = await client.get(f"/purchases/{order_id}")

    assert failed.status_code == 503
    assert detail.status_code == 200
    assert detail.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_should_cancel_order_in_draft_status() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/purchases", json=_build_order_payload())
        order_id = created.json()["id"]
        response = await client.patch(f"/purchases/{order_id}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_should_cancel_order_in_confirmed_status() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/purchases", json=_build_order_payload())
        order_id = created.json()["id"]
        await client.patch(f"/purchases/{order_id}/confirm")
        response = await client.patch(f"/purchases/{order_id}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_should_return_422_when_cancelling_received_order() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/purchases", json=_build_order_payload())
        order_id = created.json()["id"]
        await client.patch(f"/purchases/{order_id}/confirm")
        await client.patch(f"/purchases/{order_id}/receive")
        response = await client.patch(f"/purchases/{order_id}/cancel")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_should_return_403_when_vendedor_tries_to_access_purchases() -> None:
    service = FakePurchaseOrderService()
    app = _build_app(service, _build_user(RoleEnum.vendedor))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/purchases")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_should_return_403_when_bodeguero_tries_to_confirm_order() -> None:
    service = FakePurchaseOrderService()
    admin_app = _build_app(service, _build_user(RoleEnum.admin))

    async with AsyncClient(transport=ASGITransport(app=admin_app), base_url="http://test") as client:
        created = await client.post("/purchases", json=_build_order_payload())
        order_id = created.json()["id"]

    bodeguero_app = _build_app(service, _build_user(RoleEnum.bodeguero))
    async with AsyncClient(transport=ASGITransport(app=bodeguero_app), base_url="http://test") as client:
        response = await client.patch(f"/purchases/{order_id}/confirm")

    assert response.status_code == 403
