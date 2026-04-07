from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from bson import ObjectId
from bson.decimal128 import Decimal128
from motor.motor_asyncio import AsyncIOMotorDatabase

from auth.schemas import RoleEnum
from reports.schemas import DashboardResponse, TopCustomer, TopProduct
from reports.utils.masking import mask_identification


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


class DashboardService:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.sales_collection = database["sales"]
        self.stock_levels_collection = database["stock_levels"]

    async def get_dashboard_summary(
        self,
        *,
        from_date: datetime,
        to_date: datetime,
        role: RoleEnum,
        user_id: str,
    ) -> DashboardResponse:
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
                "$facet": {
                    "totals": [
                        {
                            "$group": {
                                "_id": None,
                                "total_sales_amount": {"$sum": "$total"},
                                "total_transactions": {"$sum": 1},
                            }
                        }
                    ],
                    "top_products": [
                        {"$unwind": "$lines"},
                        {
                            "$group": {
                                "_id": "$lines.product_id",
                                "product_name": {"$first": "$lines.product_name"},
                                "total_quantity": {"$sum": "$lines.quantity"},
                                "total_amount": {"$sum": "$lines.subtotal"},
                            }
                        },
                        {"$sort": {"total_quantity": -1}},
                        {"$limit": 5},
                    ],
                    "top_customers": [
                        {
                            "$group": {
                                "_id": "$customer_id",
                                "customer_name": {"$first": "$customer_name"},
                                "identification": {"$first": "$customer_identification"},
                                "total_purchases": {"$sum": 1},
                                "total_amount": {"$sum": "$total"},
                            }
                        },
                        {"$sort": {"total_amount": -1}},
                        {"$limit": 5},
                    ],
                }
            },
        ]

        aggregated = await self.sales_collection.aggregate(pipeline).to_list(length=1)
        payload = aggregated[0] if aggregated else {}

        totals = payload.get("totals", [])
        totals_item = totals[0] if totals else {}

        total_sales_amount = _to_decimal(totals_item.get("total_sales_amount", Decimal("0")))
        total_transactions = int(totals_item.get("total_transactions", 0))
        average_ticket = (
            total_sales_amount / total_transactions if total_transactions > 0 else Decimal("0")
        )

        top_products: list[TopProduct] = []
        for item in payload.get("top_products", []):
            top_products.append(
                TopProduct(
                    product_id=str(item.get("_id", "")),
                    product_name=str(item.get("product_name", "")),
                    total_quantity=int(item.get("total_quantity", 0)),
                    total_amount=_to_decimal(item.get("total_amount", Decimal("0"))),
                )
            )

        top_customers: list[TopCustomer] = []
        if role == RoleEnum.admin:
            for item in payload.get("top_customers", []):
                masked = mask_identification(str(item.get("identification", "")))
                top_customers.append(
                    TopCustomer(
                        customer_name=str(item.get("customer_name", "")),
                        identification_masked=masked,
                        total_purchases=int(item.get("total_purchases", 0)),
                        total_amount=_to_decimal(item.get("total_amount", Decimal("0"))),
                    )
                )

        low_stock_count = await self.stock_levels_collection.count_documents({"low_stock": True})

        return DashboardResponse(
            total_sales_amount=total_sales_amount,
            total_transactions=total_transactions,
            average_ticket=average_ticket,
            top_products=top_products,
            top_customers=top_customers,
            low_stock_count=low_stock_count,
            period_from=from_date,
            period_to=to_date,
        )
