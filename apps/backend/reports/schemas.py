from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class GranularityEnum(str, Enum):
    day = "day"
    week = "week"
    month = "month"


class TopProduct(BaseModel):
    model_config = ConfigDict(strict=True)

    product_id: str = Field(description="ID del producto.")
    product_name: str = Field(description="Nombre del producto mas vendido.")
    total_quantity: int = Field(description="Total de unidades vendidas en el periodo.")
    total_amount: Decimal = Field(
        decimal_places=2,
        description="Ingresos generados por este producto en el periodo.",
    )


class TopCustomer(BaseModel):
    model_config = ConfigDict(strict=True)

    customer_name: str = Field(description="Nombre del cliente. PII bajo LOPDP.")
    identification_masked: str = Field(
        description="Identificacion enmascarada: *** + ultimos 4 digitos.",
    )
    total_purchases: int = Field(description="Numero de compras en el periodo.")
    total_amount: Decimal = Field(decimal_places=2, description="Total comprado en el periodo.")


class DashboardResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    total_sales_amount: Decimal = Field(
        decimal_places=2,
        description="Suma total de ventas confirmadas en el periodo.",
    )
    total_transactions: int = Field(description="Numero de ventas confirmadas en el periodo.")
    average_ticket: Decimal = Field(
        decimal_places=2,
        description="Ticket promedio. 0 si no hay ventas.",
    )
    top_products: list[TopProduct] = Field(
        description="Los 5 productos mas vendidos. Maximo 5 items.",
    )
    top_customers: list[TopCustomer] = Field(
        description="Los 5 clientes por volumen. Vacio para vendedor.",
    )
    low_stock_count: int = Field(description="Numero de productos con low_stock: true.")
    period_from: datetime = Field(description="Inicio del periodo consultado.")
    period_to: datetime = Field(description="Fin del periodo consultado.")


class SalesReportEntry(BaseModel):
    model_config = ConfigDict(strict=True)

    date: str = Field(
        description="Fecha agrupada. dia: YYYY-MM-DD, semana: YYYY-WNN, mes: YYYY-MM.",
    )
    transactions: int = Field(description="Numero de ventas en el periodo.")
    subtotal_before_tax: Decimal = Field(decimal_places=2, description="Total antes de IVA.")
    tax_amount: Decimal = Field(decimal_places=2, description="Total de IVA.")
    total: Decimal = Field(decimal_places=2, description="Total con IVA.")


class SalesReportResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    entries: list[SalesReportEntry] = Field(description="Entradas del reporte.")
    grand_total: Decimal = Field(
        decimal_places=2,
        description="Total acumulado del periodo completo.",
    )
    total_transactions: int = Field(description="Total de transacciones del periodo.")


class InventoryReportEntry(BaseModel):
    model_config = ConfigDict(strict=True)

    product_id: str = Field(description="ID del producto.")
    product_name: str = Field(description="Nombre del producto.")
    available_quantity: int = Field(description="Stock disponible actual.")
    unit_cost: Decimal = Field(decimal_places=2, description="Precio de costo. Solo para admin.")
    total_value: Decimal = Field(
        decimal_places=2,
        description="Valorizacion: available_quantity x unit_cost.",
    )
    low_stock: bool = Field(description="Indicador de stock bajo.")
    units_sold: int = Field(
        default=0,
        description="Unidades vendidas en el periodo (si se especifico rango de fechas).",
    )
    rotation_rate: Decimal = Field(
        decimal_places=2,
        default=Decimal("0.00"),
        description="Rotacion: units_sold / available_quantity. 0 si sin stock.",
    )


class InventoryReportResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    entries: list[InventoryReportEntry] = Field(description="Entradas del reporte.")
    grand_total_value: Decimal = Field(
        decimal_places=2,
        description="Valorizacion total del inventario.",
    )


class CustomerReportEntry(BaseModel):
    model_config = ConfigDict(strict=True)

    customer_name: str = Field(description="Nombre del cliente. PII bajo LOPDP.")
    identification_masked: str = Field(
        description="Identificacion enmascarada: *** + ultimos 4 digitos.",
    )
    total_purchases: int = Field(description="Numero de compras en el periodo.")
    total_amount: Decimal = Field(decimal_places=2, description="Total comprado en el periodo.")
    last_purchase_at: datetime = Field(description="Fecha de la ultima compra.")


class CustomerReportResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    entries: list[CustomerReportEntry] = Field(description="Ranking de clientes.")
    period_from: datetime = Field(description="Inicio del periodo.")
    period_to: datetime = Field(description="Fin del periodo.")


class PurchasesReportEntry(BaseModel):
    model_config = ConfigDict(strict=True)

    supplier_name: str = Field(description="Nombre del proveedor.")
    total_orders: int = Field(description="Numero de ordenes recibidas.")
    total_amount: Decimal = Field(decimal_places=2, description="Total invertido en el periodo.")
    last_order_at: datetime = Field(description="Fecha de la ultima orden recibida.")


class PurchasesReportResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    entries: list[PurchasesReportEntry] = Field(description="Reporte por proveedor.")
    grand_total: Decimal = Field(
        decimal_places=2,
        description="Total invertido en compras en el periodo.",
    )
