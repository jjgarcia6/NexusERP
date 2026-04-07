from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT
from pymongo.collection import ReturnDocument


def sanitize_search_term(search: str) -> str:
    cleaned = search.replace("$", " ").replace("{", " ").replace("}", " ").strip()
    return " ".join(cleaned.split())


class CustomerRepository:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = database["customers"]

    async def create_customer(self, payload: dict[str, Any]) -> dict[str, Any]:
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

    async def find_by_id(
        self,
        customer_id: str,
        *,
        include_inactive: bool = False,
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(customer_id):
            return None

        query: dict[str, Any] = {"_id": ObjectId(customer_id)}
        if not include_inactive:
            query["is_active"] = True
        return await self.collection.find_one(query)

    async def find_by_identification(self, identification_number: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"identification_number": identification_number})

    async def find_all(
        self,
        *,
        search: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        bounded_skip = max(skip, 0)
        bounded_limit = min(max(limit, 1), 100)

        match: dict[str, Any] = {"is_active": True}
        if search:
            safe_search = sanitize_search_term(search)
            if safe_search:
                match["$or"] = [
                    {"$text": {"$search": safe_search}},
                    {"identification_number": {"$regex": safe_search, "$options": "i"}},
                ]

        items_cursor = (
            self.collection.find(match)
            .sort([("created_at", DESCENDING)])
            .skip(bounded_skip)
            .limit(bounded_limit)
        )
        items = await items_cursor.to_list(length=bounded_limit)
        total = await self.collection.count_documents(match)
        return items, total

    async def update_customer(
        self,
        customer_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(customer_id):
            return None

        update_payload = payload.copy()
        update_payload["updated_at"] = datetime.now(UTC)

        updated = await self.collection.find_one_and_update(
            {"_id": ObjectId(customer_id)},
            {"$set": update_payload},
            return_document=ReturnDocument.AFTER,
        )
        return cast(dict[str, Any] | None, updated)

    async def search_quick(self, q: str, *, limit: int = 10) -> list[dict[str, Any]]:
        safe_q = sanitize_search_term(q)
        if not safe_q:
            return []

        bounded_limit = min(max(limit, 1), 10)
        query = {
            "is_active": True,
            "$or": [
                {"name": {"$regex": safe_q, "$options": "i"}},
                {"identification_number": {"$regex": safe_q, "$options": "i"}},
            ],
        }
        projection = {
            "name": 1,
            "identification_number": 1,
            "customer_type": 1,
        }
        cursor = (
            self.collection.find(query, projection=projection)
            .sort("name", ASCENDING)
            .limit(bounded_limit)
        )
        return await cursor.to_list(length=bounded_limit)


async def ensure_customer_indexes(database: AsyncIOMotorDatabase[Any]) -> None:
    collection = database["customers"]
    await collection.create_index(
        [("identification_number", ASCENDING)],
        unique=True,
        name="customers_identification_number_uq",
    )
    await collection.create_index([("name", TEXT)], name="customers_name_text_idx")
    await collection.create_index(
        [("name", ASCENDING), ("identification_number", ASCENDING)],
        name="customers_name_identification_idx",
    )
    await collection.create_index([("is_active", ASCENDING)], name="customers_is_active_idx")
    await collection.create_index(
        [("customer_type", ASCENDING)],
        name="customers_customer_type_idx",
    )
