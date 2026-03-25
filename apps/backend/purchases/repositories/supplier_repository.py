from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING
from pymongo.collection import ReturnDocument


class SupplierRepository:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = database["suppliers"]

    async def create_supplier(self, payload: dict[str, Any]) -> dict[str, Any]:
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
        supplier_id: str,
        *,
        include_inactive: bool = False,
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(supplier_id):
            return None

        query: dict[str, Any] = {"_id": ObjectId(supplier_id)}
        if not include_inactive:
            query["is_active"] = True
        return await self.collection.find_one(query)

    async def find_by_ruc(self, ruc: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"ruc": ruc})

    async def find_by_email(self, email: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"contact_email": email})

    async def find_all(self, *, include_inactive: bool = False) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if not include_inactive:
            query["is_active"] = True
        cursor = self.collection.find(query).sort("name", ASCENDING)
        return await cursor.to_list(length=None)

    async def update_supplier(
        self,
        supplier_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(supplier_id):
            return None

        update_payload = payload.copy()
        update_payload["updated_at"] = datetime.now(UTC)

        updated = await self.collection.find_one_and_update(
            {"_id": ObjectId(supplier_id)},
            {"$set": update_payload},
            return_document=ReturnDocument.AFTER,
        )
        return cast(dict[str, Any] | None, updated)


async def ensure_supplier_indexes(database: AsyncIOMotorDatabase[Any]) -> None:
    collection = database["suppliers"]
    await collection.create_index(
        [("ruc", ASCENDING)],
        unique=True,
        sparse=True,
        name="suppliers_ruc_uq",
    )
    await collection.create_index(
        [("contact_email", ASCENDING)],
        unique=True,
        sparse=True,
        name="suppliers_contact_email_uq",
    )
    await collection.create_index([("is_active", ASCENDING)], name="suppliers_is_active_idx")
