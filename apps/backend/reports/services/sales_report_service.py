from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from bson import ObjectId
from bson.decimal128 import Decimal128
from motor.motor_asyncio import AsyncIOMotorDatabase

from auth.schemas import RoleEnum
from reports.schemas import GranularityEnum, SalesReportEntry, SalesReportResponse


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


class SalesReportService:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.sales_collection = database["sales"]

    async def get_sales_report(
        self,
        *,
        from_date: datetime,
        to_date: datetime,
        granularity: GranularityEnum,
        role: RoleEnum,
        user_id: str,
    ) -> SalesReportResponse:
        date_format = {
            GranularityEnum.day: "%Y-%m-%d",
            GranularityEnum.week: "%Y-W%V",
            GranularityEnum.month: "%Y-%m",
        }[granularity]

        match_filter: dict[str, Any] = {
            "status": "confirmed",
            "created_at": {"$gte": from_date, "$lte": to_date},
        }
        if role == RoleEnum.vendedor:
            match_filter["created_by"] = (
                ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            )

        pipeline: list[dict[str, Any]] = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": date_format, "date": "$created_at"}},
                    "transactions": {"$sum": 1},
                    "subtotal_before_tax": {"$sum": "$subtotal_before_tax"},
                    "tax_amount": {"$sum": "$tax_amount"},
                    "total": {"$sum": "$total"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        rows = await self.sales_collection.aggregate(pipeline).to_list(length=None)

        entries: list[SalesReportEntry] = []
        grand_total = Decimal("0")
        total_transactions = 0

        for row in rows:
            entry_total = _to_decimal(row.get("total", Decimal("0")))
            entry_transactions = int(row.get("transactions", 0))
            grand_total += entry_total
            total_transactions += entry_transactions

            entries.append(
                SalesReportEntry(
                    date=str(row.get("_id", "")),
                    transactions=entry_transactions,
                    subtotal_before_tax=_to_decimal(row.get("subtotal_before_tax", Decimal("0"))),
                    tax_amount=_to_decimal(row.get("tax_amount", Decimal("0"))),
                    total=entry_total,
                )
            )

        return SalesReportResponse(
            entries=entries,
            grand_total=grand_total,
            total_transactions=total_transactions,
        )
