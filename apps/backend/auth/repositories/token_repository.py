from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING


class TokenRepository:
    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = database["refresh_tokens"]

    async def save_token(self, token: str, user_id: str, expires_in_days: int) -> dict[str, Any]:
        expires_at = datetime.now(UTC) + timedelta(days=expires_in_days)
        payload: dict[str, Any] = {
            "token": token,
            "user_id": ObjectId(user_id),
            "expires_at": expires_at,
            "created_at": datetime.now(UTC),
        }
        await self.collection.insert_one(payload)
        return payload

    async def find_token(self, token: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"token": token})

    async def delete_token(self, token: str) -> int:
        result = await self.collection.delete_one({"token": token})
        return result.deleted_count

    async def delete_all_user_tokens(self, user_id: str) -> int:
        if not ObjectId.is_valid(user_id):
            return 0
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return result.deleted_count


async def ensure_token_indexes(database: AsyncIOMotorDatabase[Any]) -> None:
    collection = database["refresh_tokens"]
    await collection.create_index([("token", ASCENDING)], unique=True, name="refresh_token_uq")
    await collection.create_index([("user_id", ASCENDING)], name="refresh_user_idx")
    await collection.create_index(
        [("expires_at", ASCENDING)],
        expireAfterSeconds=0,
        name="refresh_ttl",
    )
