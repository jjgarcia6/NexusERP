from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.collection import ReturnDocument

from purchases.schemas import OrderStatusEnum


class PurchaseOrderRepository:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = database["purchase_orders"]

    async def create_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC)
        document = payload.copy()
        document.update(
            {
                "created_at": now,
                "updated_at": now,
            }
        )
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def find_by_id(self, order_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(order_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(order_id)})

    async def find_all(
        self,
        *,
        status: OrderStatusEnum | None = None,
        supplier_id: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        bounded_skip = max(skip, 0)
        bounded_limit = min(max(limit, 1), 100)

        query: dict[str, Any] = {}
        if status is not None:
            query["status"] = status.value
        if supplier_id is not None:
            if not ObjectId.is_valid(supplier_id):
                return [], 0
            query["supplier_id"] = ObjectId(supplier_id)

        total = await self.collection.count_documents(query)
        cursor = (
            self.collection.find(query)
            .sort("created_at", DESCENDING)
            .skip(bounded_skip)
            .limit(bounded_limit)
        )
        items = await cursor.to_list(length=bounded_limit)
        return items, total

    async def update_status(
        self,
        order_id: str,
        new_status: OrderStatusEnum,
        timestamp_field: str,
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(order_id):
            return None

        now = datetime.now(UTC)
        updated = await self.collection.find_one_and_update(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": new_status.value,
                    timestamp_field: now,
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return cast(dict[str, Any] | None, updated)


async def ensure_purchase_order_indexes(database: AsyncIOMotorDatabase[Any]) -> None:
    collection = database["purchase_orders"]
    await collection.create_index(
        [("supplier_id", ASCENDING)], name="purchase_orders_supplier_id_idx"
    )
    await collection.create_index([("status", ASCENDING)], name="purchase_orders_status_idx")
    await collection.create_index(
        [("created_at", DESCENDING)], name="purchase_orders_created_at_idx"
    )
