from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from core.settings import Settings

motor_client: AsyncIOMotorClient[Any] | None = None
database: AsyncIOMotorDatabase[Any] | None = None


async def connect_to_mongodb(settings: Settings) -> None:
    global motor_client
    global database

    motor_client = AsyncIOMotorClient(settings.mongodb_url)
    database = motor_client[settings.mongodb_db_name]


async def disconnect_from_mongodb() -> None:
    global motor_client
    global database

    if motor_client is not None:
        motor_client.close()
    motor_client = None
    database = None


def get_database() -> AsyncIOMotorDatabase[Any]:
    if database is None:
        raise RuntimeError("MongoDB connection is not initialized")
    return database
