from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT
from pymongo.collection import ReturnDocument


def sanitize_search_term(search: str) -> str:
    cleaned = search.replace("$", " ").replace("{", " ").replace("}", " ").strip()
    return " ".join(cleaned.split())


class ProductRepository:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = database["products"]

    async def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC)
        document = payload.copy()
        document.update(
            {
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        )
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def find_by_id(self, product_id: str, *, is_active: bool = True) -> dict[str, Any] | None:
        if not ObjectId.is_valid(product_id):
            return None

        items, _ = await self.find_all(
            skip=0,
            limit=1,
            product_id=product_id,
            is_active=is_active,
        )
        return items[0] if items else None

    async def find_all(
        self,
        *,
        search: str | None = None,
        category_id: str | None = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 20,
        product_id: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        bounded_skip = max(skip, 0)
        bounded_limit = min(max(limit, 1), 100)
        match: dict[str, Any] = {"is_active": is_active}

        if product_id is not None:
            if not ObjectId.is_valid(product_id):
                return [], 0
            match["_id"] = ObjectId(product_id)

        if category_id is not None:
            if not ObjectId.is_valid(category_id):
                return [], 0
            match["category_id"] = ObjectId(category_id)

        if search:
            safe_search = sanitize_search_term(search)
            if safe_search:
                match["$text"] = {"$search": safe_search}

        sort_stage: dict[str, Any] = {"created_at": DESCENDING}
        if "$text" in match:
            sort_stage = {"score": {"$meta": "textScore"}, "created_at": DESCENDING}

        pipeline: list[dict[str, Any]] = [
            {"$match": match},
            {
                "$lookup": {
                    "from": "categories",
                    "localField": "category_id",
                    "foreignField": "_id",
                    "as": "category",
                }
            },
            {"$unwind": {"path": "$category", "preserveNullAndEmptyArrays": True}},
            {"$addFields": {"category_name": {"$ifNull": ["$category.name", ""]}}},
            {
                "$project": {
                    "category": 0,
                }
            },
            {
                "$facet": {
                    "items": [
                        {"$sort": sort_stage},
                        {"$skip": bounded_skip},
                        {"$limit": bounded_limit},
                    ],
                    "count": [{"$count": "total"}],
                }
            },
        ]

        aggregation = await self.collection.aggregate(pipeline).to_list(length=1)
        if not aggregation:
            return [], 0
        items = aggregation[0].get("items", [])
        count_data = aggregation[0].get("count", [])
        total = int(count_data[0]["total"]) if count_data else 0
        return items, total

    async def update_product(
        self,
        product_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(product_id):
            return None
        update_payload = payload.copy()
        update_payload["updated_at"] = datetime.now(UTC)
        await self.collection.find_one_and_update(
            {"_id": ObjectId(product_id), "is_active": True},
            {"$set": update_payload},
            return_document=ReturnDocument.AFTER,
        )
        return await self.find_by_id(product_id, is_active=False)

    async def find_by_sku(self, sku: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"sku": sku})


async def ensure_product_indexes(database: AsyncIOMotorDatabase[Any]) -> None:
    collection = database["products"]
    await collection.create_index([("name", TEXT), ("description", TEXT)], name="products_text_idx")
    await collection.create_index([("category_id", ASCENDING)], name="products_category_id_idx")
    await collection.create_index([("is_active", ASCENDING)], name="products_is_active_idx")
    await collection.create_index(
        [("sku", ASCENDING)],
        unique=True,
        sparse=True,
        name="products_sku_uq",
    )
