from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument


class InvoiceSequenceRepository:
    def __init__(self, db: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = db["invoice_sequences"]

    async def initialize_sequence(self, point_of_sale: str) -> None:
        # Inicializa el documento base si no existe
        await self.collection.update_one(
            {"point_of_sale": point_of_sale},
            {"$setOnInsert": {"last_sequence": 0, "updated_at": datetime.utcnow()}},
            upsert=True,
        )

    async def get_next_sequence(self, point_of_sale: str) -> str:
        doc = await self.collection.find_one_and_update(
            {"point_of_sale": point_of_sale},
            {"$inc": {"last_sequence": 1}, "$set": {"updated_at": datetime.utcnow()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        sequence = doc["last_sequence"]
        return f"{point_of_sale}-{sequence:09d}"


async def ensure_invoice_sequence_initialized(
    db: AsyncIOMotorDatabase[Any],
    point_of_sale: str,
) -> None:
    repository = InvoiceSequenceRepository(db)
    await repository.initialize_sequence(point_of_sale)
