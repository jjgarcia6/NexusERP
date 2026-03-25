from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING


class StockMovementRepository:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = database["stock_movements"]

    async def create_movement(self, data: dict[str, Any]) -> dict[str, Any]:
        document = data.copy()
        document["created_at"] = datetime.now(UTC)
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def find_all(
        self,
        *,
        product_id: str | None,
        movement_type: str | None,
        from_date: datetime | None,
        to_date: datetime | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        bounded_skip = max(skip, 0)
        bounded_limit = min(max(limit, 1), 100)

        query: dict[str, Any] = {}
        if product_id is not None:
            if not ObjectId.is_valid(product_id):
                return [], 0
            query["product_id"] = ObjectId(product_id)
        if movement_type is not None:
            query["type"] = movement_type
        if from_date is not None or to_date is not None:
            created_at_filter: dict[str, Any] = {}
            if from_date is not None:
                created_at_filter["$gte"] = from_date
            if to_date is not None:
                created_at_filter["$lte"] = to_date
            query["created_at"] = created_at_filter

        total = await self.collection.count_documents(query)
        cursor = (
            self.collection.find(query)
            .sort("created_at", DESCENDING)
            .skip(bounded_skip)
            .limit(bounded_limit)
        )
        items = cast(list[dict[str, Any]], await cursor.to_list(length=bounded_limit))
        return items, total


async def ensure_stock_movement_indexes(database: AsyncIOMotorDatabase[Any]) -> None:
    collection = database["stock_movements"]
    await collection.create_index(
        [("product_id", ASCENDING), ("created_at", DESCENDING)],
        name="stock_movements_product_created_idx",
    )
    await collection.create_index(
        [("product_id", ASCENDING), ("type", ASCENDING)],
        name="stock_movements_product_type_idx",
    )
    await collection.create_index(
        [("reference_id", ASCENDING)],
        sparse=True,
        name="stock_movements_reference_id_idx",
    )
