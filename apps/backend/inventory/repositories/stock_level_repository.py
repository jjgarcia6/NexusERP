from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING
from pymongo.collection import ReturnDocument


class StockLevelRepository:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = database["stock_levels"]

    async def find_by_product_id(self, product_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(product_id):
            return None
        return await self.collection.find_one({"product_id": ObjectId(product_id)})

    async def find_all(
        self,
        *,
        low_stock: bool | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        bounded_skip = max(skip, 0)
        bounded_limit = min(max(limit, 1), 100)

        match_stock: dict[str, Any] = {}
        if low_stock is not None:
            match_stock["low_stock"] = low_stock

        pipeline: list[dict[str, Any]] = [
            {"$match": match_stock},
            {
                "$lookup": {
                    "from": "products",
                    "localField": "product_id",
                    "foreignField": "_id",
                    "as": "product",
                }
            },
            {"$unwind": {"path": "$product", "preserveNullAndEmptyArrays": False}},
            {"$match": {"product.is_active": True}},
            {
                "$addFields": {
                    "product_name": {"$ifNull": ["$product.name", "$product_name"]},
                }
            },
            {"$project": {"product": 0}},
            {
                "$facet": {
                    "items": [
                        {"$sort": {"updated_at": -1}},
                        {"$skip": bounded_skip},
                        {"$limit": bounded_limit},
                    ],
                    "count": [{"$count": "total"}],
                }
            },
        ]

        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if not result:
            return [], 0

        items = cast(list[dict[str, Any]], result[0].get("items", []))
        count_data = cast(list[dict[str, Any]], result[0].get("count", []))
        total = int(count_data[0]["total"]) if count_data else 0
        return items, total

    async def create_level(
        self,
        product_id: str,
        product_name: str,
        quantity: int,
        min_stock: int,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        document: dict[str, Any] = {
            "product_id": ObjectId(product_id),
            "product_name": product_name,
            "available_quantity": quantity,
            "min_stock": min_stock,
            "low_stock": quantity < min_stock,
            "updated_at": now,
        }
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def increment_quantity(
        self,
        product_id: str,
        delta: int,
        min_stock: int,
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(product_id):
            return None

        now = datetime.now(UTC)
        updated = await self.collection.find_one_and_update(
            {"product_id": ObjectId(product_id)},
            [
                {
                    "$set": {
                        "available_quantity": {"$add": ["$available_quantity", delta]},
                        "min_stock": min_stock,
                        "updated_at": now,
                    }
                },
                {
                    "$set": {
                        "low_stock": {"$lt": ["$available_quantity", "$min_stock"]},
                    }
                },
            ],
            return_document=ReturnDocument.AFTER,
        )
        return cast(dict[str, Any] | None, updated)

    async def update_min_stock(self, product_id: str, min_stock: int) -> dict[str, Any] | None:
        if not ObjectId.is_valid(product_id):
            return None

        updated = await self.collection.find_one_and_update(
            {"product_id": ObjectId(product_id)},
            [
                {
                    "$set": {
                        "min_stock": min_stock,
                        "updated_at": datetime.now(UTC),
                    }
                },
                {
                    "$set": {
                        "low_stock": {"$lt": ["$available_quantity", "$min_stock"]},
                    }
                },
            ],
            return_document=ReturnDocument.AFTER,
        )
        return cast(dict[str, Any] | None, updated)


async def ensure_stock_level_indexes(database: AsyncIOMotorDatabase[Any]) -> None:
    collection = database["stock_levels"]
    await collection.create_index(
        [("product_id", ASCENDING)],
        unique=True,
        name="stock_levels_product_id_uq",
    )
    await collection.create_index([("low_stock", ASCENDING)], name="stock_levels_low_stock_idx")
