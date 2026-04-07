from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException, status
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth.dependencies import get_current_user  # noqa: E402
from auth.schemas import RoleEnum, UserResponse  # noqa: E402
from sales.dependencies import get_point_of_sale, get_sale_service  # noqa: E402
from sales.routers.sales_router import router as sales_router  # noqa: E402
from sales.schemas import (  # noqa: E402
    PaymentMethodEnum,
    SaleLineRequest,
    SaleLineResponse,
    SaleListResponse,
    SaleRequest,
    SaleResponse,
    SaleStatusEnum,
    TAX_RATE,
)


class FakeSalesService:
    def __init__(self) -> None:
        self.customers = {
            'cust-1': {
                'id': 'cust-1',
                'name': 'Cliente Activo',
                'identification': '0912345678',
                'is_active': True,
            },
            'cust-2': {
                'id': 'cust-2',
                'name': 'Cliente Inactivo',
                'identification': '0999999999',
                'is_active': False,
            },
        }
        self.products = {
            'prd-1': {'id': 'prd-1', 'name': 'Producto 1', 'is_active': True, 'price': Decimal('10.00')},
            'prd-2': {'id': 'prd-2', 'name': 'Producto 2', 'is_active': True, 'price': Decimal('5.00')},
            'prd-3': {'id': 'prd-3', 'name': 'Producto Inactivo', 'is_active': False, 'price': Decimal('3.00')},
        }
        self.stock = {
            'prd-1': 100,
            'prd-2': 100,
            'prd-3': 100,
        }
        self.sales: dict[str, SaleResponse] = {}
        self.inventory_should_fail = False
        self.invoice_should_fail = False
        self._sequence = 0
        self._sequence_lock = asyncio.Lock()

    async def create_sale(self, sale_data: SaleRequest, *, created_by: str) -> SaleResponse:
        _ = created_by
        customer = self.customers.get(sale_data.customer_id)
        if customer is None or not customer['is_active']:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='El cliente especificado no está activo',
            )

        lines: list[SaleLineResponse] = []
        subtotal_before_tax = Decimal('0.00')
        for line in sale_data.lines:
            product = self.products.get(line.product_id)
            if product is None or not product['is_active']:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f'Producto inactivo: {line.product_id}',
                )
            unit_price = Decimal(str(product['price']))
            subtotal = unit_price * Decimal(line.quantity)
            subtotal_before_tax += subtotal
            lines.append(
                SaleLineResponse(
                    product_id=line.product_id,
                    product_name=str(product['name']),
                    quantity=line.quantity,
                    unit_price=unit_price,
                    subtotal=subtotal,
                )
            )

        tax_amount = subtotal_before_tax * TAX_RATE
        total = subtotal_before_tax + tax_amount
        now = datetime.now(UTC)
        sale_id = f"sale-{len(self.sales) + 1}"
        sale = SaleResponse(
            id=sale_id,
            customer_id=sale_data.customer_id,
            customer_name=str(customer['name']),
            customer_identification=str(customer['identification']),
            status=SaleStatusEnum.draft,
            invoice_number=None,
            payment_method=sale_data.payment_method,
            lines=lines,
            subtotal_before_tax=subtotal_before_tax,
            tax_rate=TAX_RATE,
            tax_amount=tax_amount,
            total=total,
            notes=sale_data.notes,
            confirmed_at=None,
            cancelled_at=None,
            created_at=now,
            updated_at=now,
        )
        self.sales[sale_id] = sale
        return sale

    async def list_sales(
        self,
        status_filter: str | None,
        customer_id: str | None,
        _from: str | None,
        _to: str | None,
        skip: int,
        limit: int,
    ) -> SaleListResponse:
        items = list(self.sales.values())
        if status_filter is not None:
            items = [sale for sale in items if sale.status.value == status_filter]
        if customer_id is not None:
            items = [sale for sale in items if sale.customer_id == customer_id]
        total = len(items)
        page = items[skip : skip + limit]
        return SaleListResponse(items=page, total=total, skip=skip, limit=limit)

    async def get_sale(self, sale_id: str) -> SaleResponse:
        sale = self.sales.get(sale_id)
        if sale is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Venta no encontrada')
        return sale

    async def confirm_sale(self, sale_id: str, user_id: str, point_of_sale: str) -> SaleResponse:
        _ = user_id
        sale = await self.get_sale(sale_id)
        if sale.status != SaleStatusEnum.draft:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Solo se pueden confirmar ventas en estado draft',
            )

        required: dict[str, int] = {}
        for line in sale.lines:
            required[line.product_id] = required.get(line.product_id, 0) + line.quantity

        for product_id, quantity in required.items():
            if self.stock.get(product_id, 0) < quantity:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f'Stock insuficiente para producto {product_id}',
                )

        if self.inventory_should_fail:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Error al decrementar stock',
            )

        for product_id, quantity in required.items():
            self.stock[product_id] -= quantity

        if self.invoice_should_fail:
            for product_id, quantity in required.items():
                self.stock[product_id] += quantity
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='No se pudo generar comprobante',
            )

        async with self._sequence_lock:
            self._sequence += 1
            sequence = self._sequence

        now = datetime.now(UTC)
        updated = sale.model_copy(
            update={
                'status': SaleStatusEnum.confirmed,
                'invoice_number': f'{point_of_sale}-{sequence:09d}',
                'confirmed_at': now,
                'updated_at': now,
            }
        )
        self.sales[sale_id] = updated
        return updated

    async def cancel_sale(self, sale_id: str, user_id: str) -> SaleResponse:
        _ = user_id
        sale = await self.get_sale(sale_id)
        if sale.status != SaleStatusEnum.confirmed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Solo se pueden cancelar ventas confirmadas',
            )

        for line in sale.lines:
            self.stock[line.product_id] = self.stock.get(line.product_id, 0) + line.quantity

        now = datetime.now(UTC)
        updated = sale.model_copy(
            update={
                'status': SaleStatusEnum.cancelled,
                'cancelled_at': now,
                'updated_at': now,
            }
        )
        self.sales[sale_id] = updated
        return updated


def _build_user(role: RoleEnum) -> UserResponse:
    return UserResponse(
        id=f'{role.value}-1',
        email=f'{role.value}@nexus.example.com',
        full_name=f'{role.value.title()} User',
        role=role,
        is_active=True,
        created_at=datetime.now(UTC),
    )


def _build_app(service: FakeSalesService, user: UserResponse) -> FastAPI:
    app = FastAPI()
    app.include_router(sales_router, prefix='/sales')
    app.dependency_overrides[get_sale_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_point_of_sale] = lambda: '001-001'
    return app


def _sale_payload(
    *,
    customer_id: str = 'cust-1',
    lines: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        'customer_id': customer_id,
        'payment_method': 'cash',
        'lines': lines
        or [
            {
                'product_id': 'prd-1',
                'quantity': 2,
            }
        ],
        'notes': 'Venta de prueba',
    }


def _sale_request(
    *,
    customer_id: str = 'cust-1',
    lines: list[dict[str, Any]] | None = None,
) -> SaleRequest:
    requested_lines = lines or [{'product_id': 'prd-1', 'quantity': 2}]
    return SaleRequest(
        customer_id=customer_id,
        payment_method=PaymentMethodEnum.cash,
        lines=[SaleLineRequest(**line) for line in requested_lines],
        notes='Venta de prueba',
    )


@pytest.mark.asyncio
async def test_should_create_sale_draft_with_correct_tax_calculation() -> None:
    service = FakeSalesService()
    sale = await service.create_sale(_sale_request(), created_by='seller-1')

    assert sale.status == SaleStatusEnum.draft
    assert sale.subtotal_before_tax == Decimal('20.00')
    assert sale.tax_amount == Decimal('2.4000')
    assert sale.total == Decimal('22.4000')


@pytest.mark.asyncio
async def test_should_return_422_when_customer_is_inactive() -> None:
    service = FakeSalesService()

    with pytest.raises(HTTPException) as exc_info:
        await service.create_sale(_sale_request(customer_id='cust-2'), created_by='seller-1')

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_should_return_422_when_product_in_line_is_inactive() -> None:
    service = FakeSalesService()

    with pytest.raises(HTTPException) as exc_info:
        await service.create_sale(
            _sale_request(lines=[{'product_id': 'prd-3', 'quantity': 1}]),
            created_by='seller-1',
        )

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_should_confirm_sale_and_decrement_stock() -> None:
    service = FakeSalesService()
    initial_stock = service.stock['prd-1']
    created = await service.create_sale(_sale_request(), created_by='seller-1')
    confirmed = await service.confirm_sale(created.id, 'seller-1', '001-001')

    assert confirmed.status == SaleStatusEnum.confirmed
    assert service.stock['prd-1'] == initial_stock - 2


@pytest.mark.asyncio
async def test_should_return_422_when_stock_is_insufficient_for_any_line() -> None:
    service = FakeSalesService()
    service.stock['prd-1'] = 1
    created = await service.create_sale(_sale_request(), created_by='seller-1')

    with pytest.raises(HTTPException) as exc_info:
        await service.confirm_sale(created.id, 'seller-1', '001-001')

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_should_not_modify_any_stock_when_one_product_has_insufficient_stock() -> None:
    service = FakeSalesService()
    service.stock['prd-1'] = 10
    service.stock['prd-2'] = 0
    payload = _sale_request(
        lines=[
            {'product_id': 'prd-1', 'quantity': 2},
            {'product_id': 'prd-2', 'quantity': 1},
        ]
    )
    created = await service.create_sale(payload, created_by='seller-1')

    with pytest.raises(HTTPException) as exc_info:
        await service.confirm_sale(created.id, 'seller-1', '001-001')

    assert exc_info.value.status_code == 422
    assert service.stock['prd-1'] == 10
    assert service.stock['prd-2'] == 0


@pytest.mark.asyncio
async def test_should_generate_unique_invoice_numbers_for_concurrent_confirmations() -> None:
    service = FakeSalesService()
    service.stock['prd-1'] = 100
    created_sales = [await service.create_sale(_sale_request(), created_by='seller-1') for _ in range(5)]
    responses = await asyncio.gather(
        *[service.confirm_sale(item.id, 'seller-1', '001-001') for item in created_sales]
    )

    invoice_numbers = [resp.invoice_number for resp in responses]
    assert len(set(invoice_numbers)) == 5


@pytest.mark.asyncio
async def test_should_return_503_when_inventory_service_fails_during_confirm() -> None:
    service = FakeSalesService()
    service.inventory_should_fail = True
    initial_stock = service.stock['prd-1']
    created = await service.create_sale(_sale_request(), created_by='seller-1')

    with pytest.raises(HTTPException) as exc_info:
        await service.confirm_sale(created.id, 'seller-1', '001-001')

    assert exc_info.value.status_code == 503
    assert service.stock['prd-1'] == initial_stock


@pytest.mark.asyncio
async def test_should_cancel_sale_and_revert_stock() -> None:
    service = FakeSalesService()
    initial_stock = service.stock['prd-1']
    created = await service.create_sale(_sale_request(), created_by='admin-1')
    await service.confirm_sale(created.id, 'admin-1', '001-001')
    cancelled = await service.cancel_sale(created.id, 'admin-1')

    assert cancelled.status == SaleStatusEnum.cancelled
    assert service.stock['prd-1'] == initial_stock


@pytest.mark.asyncio
async def test_should_preserve_invoice_number_after_cancellation() -> None:
    service = FakeSalesService()
    created = await service.create_sale(_sale_request(), created_by='admin-1')
    confirmed = await service.confirm_sale(created.id, 'admin-1', '001-001')
    cancelled = await service.cancel_sale(created.id, 'admin-1')

    assert cancelled.invoice_number == confirmed.invoice_number


@pytest.mark.asyncio
async def test_should_return_422_when_cancelling_already_cancelled_sale() -> None:
    service = FakeSalesService()
    created = await service.create_sale(_sale_request(), created_by='admin-1')
    await service.confirm_sale(created.id, 'admin-1', '001-001')
    await service.cancel_sale(created.id, 'admin-1')

    with pytest.raises(HTTPException) as exc_info:
        await service.cancel_sale(created.id, 'admin-1')

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_should_return_403_when_vendedor_tries_to_cancel_confirmed_sale() -> None:
    service = FakeSalesService()

    admin_app = _build_app(service, _build_user(RoleEnum.admin))
    async with AsyncClient(transport=ASGITransport(app=admin_app), base_url='http://test') as client:
        created = await service.create_sale(_sale_request(), created_by='admin-1')
        sale_id = created.id
        await service.confirm_sale(sale_id, 'admin-1', '001-001')

    seller_app = _build_app(service, _build_user(RoleEnum.vendedor))
    async with AsyncClient(transport=ASGITransport(app=seller_app), base_url='http://test') as client:
        response = await client.patch(f'/sales/{sale_id}/cancel')

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_should_return_403_when_bodeguero_tries_to_create_sale() -> None:
    service = FakeSalesService()
    app = _build_app(service, _build_user(RoleEnum.bodeguero))

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response = await client.post('/sales/', json=_sale_payload())

    assert response.status_code == 403
