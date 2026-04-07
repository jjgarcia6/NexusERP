from __future__ import annotations

import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth.dependencies import get_current_user  # noqa: E402
from auth.schemas import RoleEnum, UserResponse  # noqa: E402
from reports.dependencies import (  # noqa: E402
    get_customer_report_service,
    get_dashboard_service,
    get_inventory_report_service,
    get_purchases_report_service,
    get_sales_report_service,
)
from reports.routers.reports_router import router as reports_router  # noqa: E402
from reports.schemas import (  # noqa: E402
    CustomerReportEntry,
    CustomerReportResponse,
    DashboardResponse,
    GranularityEnum,
    InventoryReportEntry,
    InventoryReportResponse,
    PurchasesReportEntry,
    PurchasesReportResponse,
    SalesReportEntry,
    SalesReportResponse,
    TopCustomer,
    TopProduct,
)


class FakeDashboardService:
    async def get_dashboard_summary(
        self,
        *,
        from_date: datetime,
        to_date: datetime,
        role: RoleEnum,
        user_id: str,
    ) -> DashboardResponse:
        _ = user_id
        is_admin = role == RoleEnum.admin
        return DashboardResponse(
            total_sales_amount=Decimal("300.00") if is_admin else Decimal("120.00"),
            total_transactions=6 if is_admin else 2,
            average_ticket=Decimal("50.00") if is_admin else Decimal("60.00"),
            top_products=[
                TopProduct(
                    product_id="prd-1",
                    product_name="Producto A",
                    total_quantity=10,
                    total_amount=Decimal("150.00"),
                )
            ],
            top_customers=[
                TopCustomer(
                    customer_name="Cliente Top",
                    identification_masked="***5678",
                    total_purchases=2,
                    total_amount=Decimal("120.00"),
                )
            ]
            if is_admin
            else [],
            low_stock_count=3,
            period_from=from_date,
            period_to=to_date,
        )


class FakeSalesReportService:
    async def get_sales_report(
        self,
        *,
        from_date: datetime,
        to_date: datetime,
        granularity: GranularityEnum,
        role: RoleEnum,
        user_id: str,
    ) -> SalesReportResponse:
        _ = from_date
        _ = to_date
        _ = user_id

        if granularity == GranularityEnum.month:
            date = "2026-04"
        elif granularity == GranularityEnum.week:
            date = "2026-W14"
        else:
            date = "2026-04-07"

        base_total = Decimal("80.00") if role == RoleEnum.vendedor else Decimal("200.00")
        return SalesReportResponse(
            entries=[
                SalesReportEntry(
                    date=date,
                    transactions=2 if role == RoleEnum.vendedor else 5,
                    subtotal_before_tax=base_total,
                    tax_amount=base_total * Decimal("0.12"),
                    total=base_total * Decimal("1.12"),
                )
            ],
            grand_total=base_total * Decimal("1.12"),
            total_transactions=2 if role == RoleEnum.vendedor else 5,
        )


class FakeInventoryReportService:
    async def get_inventory_report(
        self,
        *,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> InventoryReportResponse:
        _ = from_date
        _ = to_date
        entry_a = InventoryReportEntry(
            product_id="prd-1",
            product_name="Producto A",
            available_quantity=10,
            unit_cost=Decimal("10.00"),
            total_value=Decimal("100.00"),
            low_stock=False,
            units_sold=4,
            rotation_rate=Decimal("0.40"),
        )
        entry_b = InventoryReportEntry(
            product_id="prd-2",
            product_name="Producto B",
            available_quantity=5,
            unit_cost=Decimal("10.00"),
            total_value=Decimal("50.00"),
            low_stock=True,
            units_sold=1,
            rotation_rate=Decimal("0.20"),
        )
        return InventoryReportResponse(entries=[entry_a, entry_b], grand_total_value=Decimal("150.00"))


class FakeCustomerReportService:
    async def get_customer_report(
        self,
        *,
        from_date: datetime,
        to_date: datetime,
        limit: int,
    ) -> CustomerReportResponse:
        _ = limit
        return CustomerReportResponse(
            entries=[
                CustomerReportEntry(
                    customer_name="Cliente Uno",
                    identification_masked="***1234",
                    total_purchases=3,
                    total_amount=Decimal("90.00"),
                    last_purchase_at=datetime(2026, 4, 6, tzinfo=UTC),
                )
            ],
            period_from=from_date,
            period_to=to_date,
        )


class FakePurchasesReportService:
    async def get_purchases_report(
        self,
        *,
        from_date: datetime,
        to_date: datetime,
    ) -> PurchasesReportResponse:
        _ = from_date
        _ = to_date
        return PurchasesReportResponse(
            entries=[
                PurchasesReportEntry(
                    supplier_name="Proveedor Recibido",
                    total_orders=2,
                    total_amount=Decimal("250.00"),
                    last_order_at=datetime(2026, 4, 5, tzinfo=UTC),
                )
            ],
            grand_total=Decimal("250.00"),
        )


def _build_user(role: RoleEnum, user_id: str) -> UserResponse:
    return UserResponse(
        id=user_id,
        email=f"{role.value}@nexus.example.com",
        full_name=f"{role.value.title()} User",
        role=role,
        is_active=True,
        created_at=datetime.now(UTC),
    )


def _build_app(*, role: RoleEnum, user_id: str = "user-1") -> FastAPI:
    app = FastAPI()
    app.include_router(reports_router, prefix="/reports")

    app.dependency_overrides[get_current_user] = lambda: _build_user(role, user_id)
    app.dependency_overrides[get_dashboard_service] = lambda: FakeDashboardService()
    app.dependency_overrides[get_sales_report_service] = lambda: FakeSalesReportService()
    app.dependency_overrides[get_inventory_report_service] = lambda: FakeInventoryReportService()
    app.dependency_overrides[get_customer_report_service] = lambda: FakeCustomerReportService()
    app.dependency_overrides[get_purchases_report_service] = lambda: FakePurchasesReportService()

    return app


@pytest.mark.asyncio
async def test_should_return_dashboard_with_correct_totals_for_admin() -> None:
    app = _build_app(role=RoleEnum.admin)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_sales_amount"] == "300.00"
    assert payload["total_transactions"] == 6
    assert len(payload["top_customers"]) == 1


@pytest.mark.asyncio
async def test_should_return_dashboard_with_only_own_sales_for_vendedor() -> None:
    app = _build_app(role=RoleEnum.vendedor, user_id="seller-1")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_sales_amount"] == "120.00"
    assert payload["total_transactions"] == 2


@pytest.mark.asyncio
async def test_should_return_empty_top_customers_for_vendedor() -> None:
    app = _build_app(role=RoleEnum.vendedor, user_id="seller-1")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/")

    assert response.status_code == 200
    assert response.json()["top_customers"] == []


@pytest.mark.asyncio
async def test_should_return_403_when_bodeguero_accesses_dashboard() -> None:
    app = _build_app(role=RoleEnum.bodeguero)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_should_return_sales_report_grouped_by_day() -> None:
    app = _build_app(role=RoleEnum.admin)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/sales", params={"granularity": "day"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["entries"][0]["date"] == "2026-04-07"


@pytest.mark.asyncio
async def test_should_return_sales_report_grouped_by_month() -> None:
    app = _build_app(role=RoleEnum.admin)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/sales", params={"granularity": "month"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["entries"][0]["date"] == "2026-04"


@pytest.mark.asyncio
async def test_should_filter_vendedor_sales_in_sales_report() -> None:
    app = _build_app(role=RoleEnum.vendedor, user_id="seller-1")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/sales")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_transactions"] == 2
    assert payload["grand_total"] == "89.6000"


@pytest.mark.asyncio
async def test_should_return_inventory_report_with_correct_total_value() -> None:
    app = _build_app(role=RoleEnum.admin)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/inventory")

    assert response.status_code == 200
    payload = response.json()
    assert payload["grand_total_value"] == "150.00"


@pytest.mark.asyncio
async def test_should_return_customer_report_with_masked_identification() -> None:
    app = _build_app(role=RoleEnum.admin)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/customers")

    assert response.status_code == 200
    payload = response.json()
    assert payload["entries"][0]["identification_masked"] == "***1234"


@pytest.mark.asyncio
async def test_should_return_403_when_vendedor_accesses_customer_report() -> None:
    app = _build_app(role=RoleEnum.vendedor)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/customers")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_should_return_purchases_report_with_only_received_orders() -> None:
    app = _build_app(role=RoleEnum.admin)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reports/purchases")

    assert response.status_code == 200
    payload = response.json()
    assert payload["entries"] == [
        {
            "supplier_name": "Proveedor Recibido",
            "total_orders": 2,
            "total_amount": "250.00",
            "last_order_at": "2026-04-05T00:00:00Z",
        }
    ]


@pytest.mark.asyncio
async def test_should_return_422_when_from_is_after_to() -> None:
    app = _build_app(role=RoleEnum.admin)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/reports/sales",
            params={
                "from": "2026-05-01T00:00:00Z",
                "to": "2026-04-01T00:00:00Z",
            },
        )

    assert response.status_code == 422
