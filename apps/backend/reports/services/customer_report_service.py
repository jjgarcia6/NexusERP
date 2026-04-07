from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from bson.decimal128 import Decimal128
from motor.motor_asyncio import AsyncIOMotorDatabase

from reports.schemas import CustomerReportEntry, CustomerReportResponse
from reports.utils.masking import mask_identification


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


class CustomerReportService:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.sales_collection = database["sales"]

    async def get_customer_report(
        self,
        *,
        from_date: datetime,
        to_date: datetime,
        limit: int,
    ) -> CustomerReportResponse:
        bounded_limit = min(max(limit, 1), 100)

        pipeline: list[dict[str, Any]] = [
            {
                "$match": {
                    "status": "confirmed",
                    "created_at": {"$gte": from_date, "$lte": to_date},
                }
            },
            {
                "$group": {
                    "_id": "$customer_id",
                    "customer_name": {"$first": "$customer_name"},
                    "customer_identification": {"$first": "$customer_identification"},
                    "total_purchases": {"$sum": 1},
                    "total_amount": {"$sum": "$total"},
                    "last_purchase_at": {"$max": "$created_at"},
                }
            },
            {"$sort": {"total_amount": -1}},
            {"$limit": bounded_limit},
        ]

        rows = await self.sales_collection.aggregate(pipeline).to_list(length=None)

        entries: list[CustomerReportEntry] = []
        for row in rows:
            entries.append(
                CustomerReportEntry(
                    customer_name=str(row.get("customer_name", "")),
                    identification_masked=mask_identification(
                        str(row.get("customer_identification", ""))
                    ),
                    total_purchases=int(row.get("total_purchases", 0)),
                    total_amount=_to_decimal(row.get("total_amount", Decimal("0"))),
                    last_purchase_at=row.get("last_purchase_at", from_date),
                )
            )

        return CustomerReportResponse(entries=entries, period_from=from_date, period_to=to_date)
