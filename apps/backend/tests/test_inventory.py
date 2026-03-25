from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth.dependencies import get_current_user  # noqa: E402
from auth.schemas import RoleEnum, UserResponse  # noqa: E402
from inventory.dependencies import get_inventory_service  # noqa: E402
from inventory.routers.inventory_router import router as inventory_router  # noqa: E402
from inventory.schemas import MovementTypeEnum, StockMovementRequest  # noqa: E402
from inventory.services.inventory_service import InventoryService  # noqa: E402
from purchases.schemas import PurchaseOrderLineResponse  # noqa: E402


class FakeProductRepository:
    def __init__(self) -> None:
        self.products: dict[str, dict[str, Any]] = {
            "prd-1": {"_id": "prd-1", "name": "Producto 1", "is_active": True, "min_stock": 5},
            "prd-2": {"_id": "prd-2", "name": "Producto 2", "is_active": True, "min_stock": 2},
            "prd-3": {"_id": "prd-3", "name": "Producto 3", "is_active": True, "min_stock": 1},
        }

    async def find_by_id(self, product_id: str, *, is_active: bool = True) -> dict[str, Any] | None:
        product = self.products.get(product_id)
        if product is None:
            return None
        if is_active and not product.get("is_active", False):
            return None
        return product


class FakeStockLevelRepository:
    def __init__(self) -> None:
        self.levels: dict[str, dict[str, Any]] = {}

    async def find_by_product_id(self, product_id: str) -> dict[str, Any] | None:
        return self.levels.get(product_id)

    async def find_all(self, *, low_stock: bool | None, skip: int, limit: int) -> tuple[list[dict[str, Any]], int]:
        items = list(self.levels.values())
        if low_stock is not None:
            items = [item for item in items if item["low_stock"] is low_stock]
        total = len(items)
        return items[skip : skip + limit], total

    async def create_level(self, product_id: str, product_name: str, quantity: int, min_stock: int) -> dict[str, Any]:
        level = {
            "_id": f"lvl-{product_id}",
            "product_id": product_id,
            "product_name": product_name,
            "available_quantity": quantity,
            "min_stock": min_stock,
            "low_stock": quantity < min_stock,
            "updated_at": datetime.now(UTC),
        }
        self.levels[product_id] = level
        return level

    async def increment_quantity(self, product_id: str, delta: int, min_stock: int) -> dict[str, Any] | None:
        level = self.levels.get(product_id)
        if level is None:
            return None
        next_quantity = int(level["available_quantity"]) + delta
        level["available_quantity"] = next_quantity
        level["min_stock"] = min_stock
        level["low_stock"] = next_quantity < min_stock
        level["updated_at"] = datetime.now(UTC)
        return level

    async def update_min_stock(self, product_id: str, min_stock: int) -> dict[str, Any] | None:
        level = self.levels.get(product_id)
        if level is None:
            return None
        level["min_stock"] = min_stock
        level["low_stock"] = int(level["available_quantity"]) < min_stock
        level["updated_at"] = datetime.now(UTC)
        return level


class FakeStockMovementRepository:
    def __init__(self) -> None:
        self.movements: list[dict[str, Any]] = []
        self.fail_on_create = False
        self.fail_after_n_creates: int | None = None

    async def create_movement(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.fail_on_create:
            raise RuntimeError("forced movement failure")
        if self.fail_after_n_creates is not None and len(self.movements) >= self.fail_after_n_creates:
            raise RuntimeError("forced movement failure after N")

        movement = data.copy()
        movement["_id"] = f"mov-{len(self.movements) + 1}"
        movement["created_at"] = datetime.now(UTC)
        self.movements.append(movement)
        return movement

    async def find_all(
        self,
        *,
        product_id: str | None,
        movement_type: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        items = self.movements
        if product_id is not None:
            items = [item for item in items if item["product_id"] == product_id]
        if movement_type is not None:
            items = [item for item in items if item["type"] == movement_type]
        if from_date is not None:
            items = [item for item in items if item["created_at"] >= from_date]
        if to_date is not None:
            items = [item for item in items if item["created_at"] <= to_date]

        total = len(items)
        return items[skip : skip + limit], total


def build_service() -> tuple[InventoryService, FakeStockLevelRepository, FakeStockMovementRepository]:
    product_repository = FakeProductRepository()
    stock_level_repository = FakeStockLevelRepository()
    stock_movement_repository = FakeStockMovementRepository()
    service = InventoryService(product_repository, stock_level_repository, stock_movement_repository)
    return service, stock_level_repository, stock_movement_repository


@pytest.mark.asyncio
async def test_should_initialize_stock_and_return_201_when_product_exists() -> None:
    service, _, movement_repo = build_service()

    result = await service.initialize_stock("prd-1", quantity=10, min_stock=3, user_id="admin-1")

    assert result["available_quantity"] == 10
    assert result["low_stock"] is False
    assert len(movement_repo.movements) == 1


@pytest.mark.asyncio
async def test_should_return_409_when_stock_already_initialized() -> None:
    service, _, _ = build_service()
    await service.initialize_stock("prd-1", quantity=5, min_stock=2, user_id="admin-1")

    with pytest.raises(HTTPException) as exc_info:
        await service.initialize_stock("prd-1", quantity=3, min_stock=1, user_id="admin-1")

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_should_register_manual_entry_and_increment_stock() -> None:
    service, _, _ = build_service()
    await service.initialize_stock("prd-1", quantity=5, min_stock=2, user_id="admin-1")

    movement = await service.register_movement(
        StockMovementRequest(
            product_id="prd-1",
            type=MovementTypeEnum.manual_entry,
            quantity=3,
            reason="Ajuste de ingreso",
        ),
        user_id="admin-1",
    )

    assert movement["quantity_after"] == 8


@pytest.mark.asyncio
async def test_should_register_manual_exit_and_decrement_stock() -> None:
    service, _, _ = build_service()
    await service.initialize_stock("prd-1", quantity=8, min_stock=2, user_id="admin-1")

    movement = await service.register_movement(
        StockMovementRequest(
            product_id="prd-1",
            type=MovementTypeEnum.manual_exit,
            quantity=2,
            reason="Salida por merma",
        ),
        user_id="admin-1",
    )

    assert movement["quantity_after"] == 6


@pytest.mark.asyncio
async def test_should_return_422_when_exit_exceeds_available_stock() -> None:
    service, _, _ = build_service()
    await service.initialize_stock("prd-1", quantity=2, min_stock=1, user_id="admin-1")

    with pytest.raises(HTTPException) as exc_info:
        await service.register_movement(
            StockMovementRequest(
                product_id="prd-1",
                type=MovementTypeEnum.manual_exit,
                quantity=5,
                reason="Salida excesiva",
            ),
            user_id="admin-1",
        )

    assert exc_info.value.status_code == 422
    assert "Disponible: 2, solicitado: 5" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_should_set_low_stock_true_when_quantity_falls_below_min_stock() -> None:
    service, level_repo, _ = build_service()
    await service.initialize_stock("prd-1", quantity=5, min_stock=4, user_id="admin-1")

    await service.register_movement(
        StockMovementRequest(
            product_id="prd-1",
            type=MovementTypeEnum.manual_exit,
            quantity=2,
            reason="Salida por traslado",
        ),
        user_id="admin-1",
    )

    level = await level_repo.find_by_product_id("prd-1")
    assert level is not None
    assert level["low_stock"] is True


@pytest.mark.asyncio
async def test_should_set_low_stock_false_when_quantity_rises_above_min_stock() -> None:
    service, level_repo, _ = build_service()
    await service.initialize_stock("prd-1", quantity=1, min_stock=3, user_id="admin-1")

    await service.register_movement(
        StockMovementRequest(
            product_id="prd-1",
            type=MovementTypeEnum.manual_entry,
            quantity=5,
            reason="Ingreso por compra",
        ),
        user_id="admin-1",
    )

    level = await level_repo.find_by_product_id("prd-1")
    assert level is not None
    assert level["low_stock"] is False


@pytest.mark.asyncio
async def test_should_revert_stock_level_when_movement_registration_fails() -> None:
    service, level_repo, movement_repo = build_service()
    await service.initialize_stock("prd-1", quantity=5, min_stock=2, user_id="admin-1")
    movement_repo.fail_on_create = True

    with pytest.raises(HTTPException) as exc_info:
        await service.register_movement(
            StockMovementRequest(
                product_id="prd-1",
                type=MovementTypeEnum.manual_entry,
                quantity=4,
                reason="Ingreso con fallo",
            ),
            user_id="admin-1",
        )

    level = await level_repo.find_by_product_id("prd-1")
    assert level is not None
    assert level["available_quantity"] == 5
    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_should_register_purchase_entries_for_all_order_lines() -> None:
    service, level_repo, movement_repo = build_service()
    lines = [
        PurchaseOrderLineResponse(
            product_id="prd-1",
            quantity=2,
            unit_cost=1,
            product_name="Producto 1",
            subtotal=2,
        ),
        PurchaseOrderLineResponse(
            product_id="prd-2",
            quantity=3,
            unit_cost=1,
            product_name="Producto 2",
            subtotal=3,
        ),
    ]

    await service.register_stock_entries("ord-1", lines)

    level1 = await level_repo.find_by_product_id("prd-1")
    level2 = await level_repo.find_by_product_id("prd-2")
    assert level1 is not None and level1["available_quantity"] == 2
    assert level2 is not None and level2["available_quantity"] == 3
    assert len(movement_repo.movements) == 2


@pytest.mark.asyncio
async def test_should_auto_initialize_stock_when_product_has_no_stock_level() -> None:
    service, level_repo, _ = build_service()

    await service.register_stock_entries(
        "ord-2",
        [
            PurchaseOrderLineResponse(
                product_id="prd-3",
                quantity=4,
                unit_cost=1,
                product_name="Producto 3",
                subtotal=4,
            )
        ],
    )

    level = await level_repo.find_by_product_id("prd-3")
    assert level is not None
    assert level["available_quantity"] == 4


@pytest.mark.asyncio
async def test_should_revert_partial_entries_when_one_line_fails_in_register_stock_entries() -> None:
    service, level_repo, movement_repo = build_service()
    movement_repo.fail_after_n_creates = 2

    lines = [
        PurchaseOrderLineResponse(product_id="prd-1", quantity=1, unit_cost=1, product_name="P1", subtotal=1),
        PurchaseOrderLineResponse(product_id="prd-2", quantity=1, unit_cost=1, product_name="P2", subtotal=1),
        PurchaseOrderLineResponse(product_id="prd-3", quantity=1, unit_cost=1, product_name="P3", subtotal=1),
        PurchaseOrderLineResponse(product_id="prd-1", quantity=1, unit_cost=1, product_name="P1", subtotal=1),
    ]

    with pytest.raises(RuntimeError):
        await service.register_stock_entries("ord-3", lines)

    level1 = await level_repo.find_by_product_id("prd-1")
    level2 = await level_repo.find_by_product_id("prd-2")
    level3 = await level_repo.find_by_product_id("prd-3")

    assert level1 is not None and level1["available_quantity"] == 0
    assert level2 is not None and level2["available_quantity"] == 0
    assert level3 is None or level3["available_quantity"] == 0


@pytest.mark.asyncio
async def test_should_return_true_from_check_stock_availability_when_stock_is_sufficient() -> None:
    service, _, _ = build_service()
    await service.initialize_stock("prd-1", quantity=6, min_stock=2, user_id="admin-1")

    result = await service.check_stock_availability("prd-1", 4)

    assert result is True


@pytest.mark.asyncio
async def test_should_return_false_from_check_stock_availability_when_stock_is_insufficient() -> None:
    service, _, _ = build_service()
    await service.initialize_stock("prd-1", quantity=1, min_stock=1, user_id="admin-1")

    result = await service.check_stock_availability("prd-1", 3)

    assert result is False


@pytest.mark.asyncio
async def test_should_recalculate_low_stock_when_min_stock_is_updated() -> None:
    _, level_repo, _ = build_service()
    await level_repo.create_level("prd-1", "Producto 1", quantity=5, min_stock=2)

    updated = await level_repo.update_min_stock("prd-1", min_stock=10)

    assert updated is not None
    assert updated["low_stock"] is True


def _build_user(role: RoleEnum) -> UserResponse:
    return UserResponse(
        id=f"{role.value}-1",
        email=f"{role.value}@nexus.example.com",
        full_name=f"{role.value.title()} User",
        role=role,
        is_active=True,
        created_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_should_return_403_when_vendedor_tries_to_register_movement() -> None:
    service, _, _ = build_service()
    await service.initialize_stock("prd-1", quantity=2, min_stock=1, user_id="admin-1")

    app = FastAPI()
    app.include_router(inventory_router, prefix="/inventory")
    app.dependency_overrides[get_inventory_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: _build_user(RoleEnum.vendedor)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/inventory/movements",
            json={
                "product_id": "prd-1",
                "type": "manual_entry",
                "quantity": 1,
                "reason": "Ingreso de prueba",
            },
        )

    assert response.status_code == 403
