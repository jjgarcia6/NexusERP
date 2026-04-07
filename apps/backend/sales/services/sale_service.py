from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status

from sales.schemas import (
    TAX_RATE,
    PaymentMethodEnum,
    SaleLineResponse,
    SaleListResponse,
    SaleRequest,
    SaleResponse,
    SaleStatusEnum,
)


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _serialize_sale(document: dict[str, Any]) -> SaleResponse:
    lines: list[SaleLineResponse] = []
    for line in document.get("lines", []):
        lines.append(
            SaleLineResponse(
                product_id=str(line["product_id"]),
                product_name=str(line["product_name"]),
                quantity=int(line["quantity"]),
                unit_price=Decimal(str(line["unit_price"])),
                subtotal=Decimal(str(line["subtotal"])),
            )
        )

    return SaleResponse(
        id=str(document["_id"]),
        customer_id=str(document["customer_id"]),
        customer_name=str(document["customer_name"]),
        customer_identification=str(document["customer_identification"]),
        status=SaleStatusEnum(str(document["status"])),
        invoice_number=(
            str(document["invoice_number"]) if document.get("invoice_number") is not None else None
        ),
        payment_method=PaymentMethodEnum(str(document["payment_method"])),
        lines=lines,
        subtotal_before_tax=Decimal(str(document["subtotal_before_tax"])),
        tax_rate=Decimal(str(document["tax_rate"])),
        tax_amount=Decimal(str(document["tax_amount"])),
        total=Decimal(str(document["total"])),
        notes=(str(document["notes"]) if document.get("notes") else None),
        confirmed_at=document.get("confirmed_at"),
        cancelled_at=document.get("cancelled_at"),
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


class SaleService:
    def __init__(
        self,
        sale_repository: Any,
        customer_repository: Any,
        product_repository: Any,
        invoice_sequence_repository: Any,
        inventory_service: Any,
    ) -> None:
        self.sale_repository = sale_repository
        self.customer_repository = customer_repository
        self.product_repository = product_repository
        self.invoice_sequence_repository = invoice_sequence_repository
        self.inventory_service = inventory_service

    async def create_sale(self, sale_data: SaleRequest, *, created_by: str) -> SaleResponse:
        customer = await self.customer_repository.find_by_id(sale_data.customer_id)
        if customer is None or not bool(customer.get("is_active", False)):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El cliente especificado no está activo",
            )

        lines: list[dict[str, Any]] = []
        for line in sale_data.lines:
            product = await self.product_repository.find_by_id(line.product_id)
            if product is None or not bool(product.get("is_active", False)):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Producto inactivo: {line.product_id}",
                )

            unit_price = Decimal(str(product["price"]))
            quantity = int(line.quantity)
            lines.append(
                {
                    "product_id": line.product_id,
                    "product_name": str(product["name"]),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "subtotal": unit_price * quantity,
                }
            )

        subtotal_before_tax = sum(item["subtotal"] for item in lines)
        tax_amount = subtotal_before_tax * TAX_RATE
        total = subtotal_before_tax + tax_amount
        now = datetime.now(UTC)

        sale_payload = {
            "customer_id": sale_data.customer_id,
            "customer_name": str(customer["name"]),
            "customer_identification": str(customer["identification_number"]),
            "status": "draft",
            "payment_method": sale_data.payment_method.value,
            "lines": lines,
            "subtotal_before_tax": subtotal_before_tax,
            "tax_rate": TAX_RATE,
            "tax_amount": tax_amount,
            "total": total,
            "notes": sale_data.notes,
            "created_by": created_by,
            "confirmed_at": None,
            "cancelled_at": None,
            "created_at": now,
            "updated_at": now,
        }
        created = await self.sale_repository.create_sale(sale_payload)
        return _serialize_sale(created)

    async def list_sales(
        self,
        status_filter: str | None,
        customer_id: str | None,
        from_date: str | None,
        to_date: str | None,
        skip: int,
        limit: int,
    ) -> SaleListResponse:
        items, total = await self.sale_repository.find_all(
            status=status_filter,
            customer_id=customer_id,
            from_date=_parse_datetime(from_date),
            to_date=_parse_datetime(to_date),
            skip=skip,
            limit=limit,
        )
        return SaleListResponse(
            items=[_serialize_sale(item) for item in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_sale(self, sale_id: str) -> SaleResponse:
        sale = await self.sale_repository.find_by_id(sale_id)
        if sale is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
        return _serialize_sale(sale)

    async def confirm_sale(self, sale_id: str, _user_id: str, point_of_sale: str) -> SaleResponse:
        sale = await self.sale_repository.find_by_id(sale_id)
        if sale is None or sale.get("status") != "draft":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Solo se pueden confirmar ventas en estado draft",
            )

        for line in sale["lines"]:
            has_stock = await self.inventory_service.check_stock_availability(
                str(line["product_id"]), int(line["quantity"])
            )
            if not has_stock:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Stock insuficiente para producto {line['product_id']}",
                )

        try:
            await self.inventory_service.register_sale_exits(sale_id, sale["lines"])
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo descontar stock para confirmar la venta",
            ) from exc

        try:
            invoice_number = await self.invoice_sequence_repository.get_next_sequence(point_of_sale)
        except Exception as exc:
            await self.inventory_service.revert_sale_exits(
                sale_id,
                sale["lines"],
                reason="Compensación por error al generar comprobante",
                reference_type="sale_confirm_compensation",
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo generar el número de comprobante",
            ) from exc

        updated = await self.sale_repository.mark_confirmed(sale_id, invoice_number)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
        return _serialize_sale(updated)

    async def cancel_sale(self, sale_id: str, _user_id: str) -> SaleResponse:
        sale = await self.sale_repository.find_by_id(sale_id)
        if sale is None or sale.get("status") != "confirmed":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Solo se pueden cancelar ventas confirmadas",
            )

        await self.inventory_service.revert_sale_exits(
            sale_id,
            sale["lines"],
            reason="Cancelación de venta confirmada",
            reference_type="sale_cancellation",
        )
        updated = await self.sale_repository.mark_cancelled(sale_id)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
        return _serialize_sale(updated)
