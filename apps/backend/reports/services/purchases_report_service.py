from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from bson.decimal128 import Decimal128
from motor.motor_asyncio import AsyncIOMotorDatabase

from reports.schemas import PurchasesReportEntry, PurchasesReportResponse


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


class PurchasesReportService:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.purchase_orders_collection = database["purchase_orders"]

    async def get_purchases_report(
        self,
        *,
        from_date: datetime,
        to_date: datetime,
    ) -> PurchasesReportResponse:
        pipeline: list[dict[str, Any]] = [
            {
                "$match": {
                    "status": "received",
                    "received_at": {"$gte": from_date, "$lte": to_date},
                }
            },
            {
                "$group": {
                    "_id": "$supplier_id",
                    "supplier_name": {"$first": "$supplier_name"},
                    "total_orders": {"$sum": 1},
                    "total_amount": {"$sum": "$total"},
                    "last_order_at": {"$max": "$received_at"},
                }
            },
            {"$sort": {"total_amount": -1}},
        ]

        rows = await self.purchase_orders_collection.aggregate(pipeline).to_list(length=None)

        entries: list[PurchasesReportEntry] = []
        grand_total = Decimal("0")

        for row in rows:
            total_amount = _to_decimal(row.get("total_amount", Decimal("0")))
            grand_total += total_amount
            entries.append(
                PurchasesReportEntry(
                    supplier_name=str(row.get("supplier_name", "")),
                    total_orders=int(row.get("total_orders", 0)),
                    total_amount=total_amount,
                    last_order_at=row.get("last_order_at", from_date),
                )
            )

        return PurchasesReportResponse(entries=entries, grand_total=grand_total)
