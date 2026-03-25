from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING
from pymongo.collection import ReturnDocument


class CategoryRepository:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = database["categories"]
        self.products_collection = database["products"]

    async def create_category(self, name: str, description: str | None) -> dict[str, Any]:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "name": name,
            "description": description,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        result = await self.collection.insert_one(payload)
        payload["_id"] = result.inserted_id
        return payload

    async def find_by_id(
        self,
        category_id: str,
        *,
        include_inactive: bool = False,
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(category_id):
            return None

        query: dict[str, Any] = {"_id": ObjectId(category_id)}
        if not include_inactive:
            query["is_active"] = True
        return await self.collection.find_one(query)

    async def find_by_name(self, name: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"name": name})

    async def find_all(self, *, include_inactive: bool = False) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if not include_inactive:
            query["is_active"] = True
        cursor = self.collection.find(query).sort("name", ASCENDING)
        return await cursor.to_list(length=None)

    async def update_category(
        self,
        category_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(category_id):
            return None

        update_payload = payload.copy()
        update_payload["updated_at"] = datetime.now(UTC)
        updated = await self.collection.find_one_and_update(
            {"_id": ObjectId(category_id), "is_active": True},
            {"$set": update_payload},
            return_document=ReturnDocument.AFTER,
        )
        return cast(dict[str, Any] | None, updated)

    async def delete_category(self, category_id: str) -> int:
        if not ObjectId.is_valid(category_id):
            return 0
        result = await self.collection.delete_one({"_id": ObjectId(category_id), "is_active": True})
        return result.deleted_count

    async def has_active_products(self, category_id: str) -> bool:
        if not ObjectId.is_valid(category_id):
            return False
        total = await self.products_collection.count_documents(
            {
                "category_id": ObjectId(category_id),
                "is_active": True,
            }
        )
        return total > 0


async def ensure_category_indexes(database: AsyncIOMotorDatabase[Any]) -> None:
    collection = database["categories"]
    await collection.create_index([("name", ASCENDING)], unique=True, name="categories_name_uq")
    await collection.create_index([("is_active", ASCENDING)], name="categories_is_active_idx")
