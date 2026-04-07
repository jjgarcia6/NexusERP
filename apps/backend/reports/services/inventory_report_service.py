from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from bson.decimal128 import Decimal128
from motor.motor_asyncio import AsyncIOMotorDatabase

from reports.schemas import InventoryReportEntry, InventoryReportResponse


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


class InventoryReportService:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.stock_levels_collection = database["stock_levels"]
        self.stock_movements_collection = database["stock_movements"]

    async def get_inventory_report(
        self,
        *,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> InventoryReportResponse:
        sales_lookup_pipeline: list[dict[str, Any]] = [
            {
                "$match": {
                    "$expr": {
                        "$and": [
                            {"$eq": ["$product_id", "$$pid"]},
                            {"$eq": ["$type", "sale_exit"]},
                        ]
                    }
                }
            },
            {"$group": {"_id": None, "units_sold": {"$sum": "$quantity"}}},
        ]

        if from_date is not None and to_date is not None:
            sales_lookup_pipeline[0]["$match"]["$expr"]["$and"].extend(
                [
                    {"$gte": ["$created_at", from_date]},
                    {"$lte": ["$created_at", to_date]},
                ]
            )

        pipeline: list[dict[str, Any]] = [
            {
                "$lookup": {
                    "from": "products",
                    "localField": "product_id",
                    "foreignField": "_id",
                    "as": "product",
                }
            },
            {"$unwind": "$product"},
            {"$match": {"product.is_active": True, "product.cost": {"$ne": None}}},
            {
                "$lookup": {
                    "from": "stock_movements",
                    "let": {"pid": "$product_id"},
                    "pipeline": sales_lookup_pipeline,
                    "as": "sales_stats",
                }
            },
            {
                "$project": {
                    "product_id": 1,
                    "product_name": "$product.name",
                    "available_quantity": 1,
                    "unit_cost": "$product.cost",
                    "total_value": {"$multiply": ["$available_quantity", "$product.cost"]},
                    "low_stock": 1,
                    "units_sold": {
                        "$ifNull": [{"$arrayElemAt": ["$sales_stats.units_sold", 0]}, 0],
                    },
                }
            },
            {"$sort": {"product_name": 1}},
        ]

        rows = await self.stock_levels_collection.aggregate(pipeline).to_list(length=None)

        entries: list[InventoryReportEntry] = []
        grand_total_value = Decimal("0")

        for row in rows:
            available_quantity = int(row.get("available_quantity", 0))
            unit_cost = _to_decimal(row.get("unit_cost", Decimal("0")))
            total_value = _to_decimal(row.get("total_value", Decimal("0")))
            units_sold = int(row.get("units_sold", 0))
            rotation_rate = (
                Decimal(units_sold) / Decimal(available_quantity)
                if available_quantity > 0
                else Decimal("0")
            )
            grand_total_value += total_value

            entries.append(
                InventoryReportEntry(
                    product_id=str(row.get("product_id", "")),
                    product_name=str(row.get("product_name", "")),
                    available_quantity=available_quantity,
                    unit_cost=unit_cost,
                    total_value=total_value,
                    low_stock=bool(row.get("low_stock", False)),
                    units_sold=units_sold,
                    rotation_rate=rotation_rate,
                )
            )

        return InventoryReportResponse(
            entries=entries,
            grand_total_value=grand_total_value,
        )
