from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING

from auth.schemas import RoleEnum


class UserRepository:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = database["users"]

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        role: RoleEnum,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "role": role.value,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        result = await self.collection.insert_one(payload)
        payload["_id"] = result.inserted_id
        return payload

    async def find_by_email(self, email: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"email": email})

    async def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(user_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(user_id)})


async def ensure_user_indexes(database: AsyncIOMotorDatabase[Any]) -> None:
    collection = database["users"]
    await collection.create_index([("email", ASCENDING)], unique=True, name="users_email_uq")
    await collection.create_index([("is_active", ASCENDING)], name="users_is_active_idx")
