from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast

from bson import ObjectId
from bson.decimal128 import Decimal128
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.collection import ReturnDocument


def _to_bson_compatible(value: Any) -> Any:
    if isinstance(value, Decimal):
        return Decimal128(value)
    if isinstance(value, dict):
        return {key: _to_bson_compatible(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_bson_compatible(item) for item in value]
    return value


class SaleRepository:
    def __init__(self, db: AsyncIOMotorDatabase[Any]) -> None:
        self.collection = db["sales"]

    async def create_indexes(self) -> None:
        await self.collection.create_index([("customer_id", ASCENDING)])
        await self.collection.create_index([("status", ASCENDING)])
        await self.collection.create_index([("created_at", DESCENDING)])
        index_name = "invoice_number_1"
        index_info = await self.collection.index_information()
        existing = cast(dict[str, Any] | None, index_info.get(index_name))
        if existing is not None:
            has_partial_filter = "partialFilterExpression" in existing
            if not has_partial_filter:
                await self.collection.drop_index(index_name)

        await self.collection.create_index(
            [("invoice_number", ASCENDING)],
            unique=True,
            partialFilterExpression={"invoice_number": {"$type": "string"}},
        )
        await self.collection.create_index([("created_by", ASCENDING)])

    async def create_sale(self, sale: dict[str, Any]) -> dict[str, Any]:
        document = sale.copy()
        now = datetime.now(UTC)
        document["created_at"] = document.get("created_at", now)
        document["updated_at"] = document.get("updated_at", now)
        document = cast(dict[str, Any], _to_bson_compatible(document))
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def find_by_id(self, sale_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(sale_id):
            return None
        document = await self.collection.find_one({"_id": ObjectId(sale_id)})
        return cast(dict[str, Any] | None, document)

    async def find_all(
        self,
        status: str | None = None,
        customer_id: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        bounded_skip = max(skip, 0)
        bounded_limit = min(max(limit, 1), 100)
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        if customer_id:
            query["customer_id"] = customer_id
        if from_date and to_date:
            query["created_at"] = {"$gte": from_date, "$lte": to_date}
        elif from_date:
            query["created_at"] = {"$gte": from_date}
        elif to_date:
            query["created_at"] = {"$lte": to_date}
        total = await self.collection.count_documents(query)
        cursor = (
            self.collection.find(query)
            .sort("created_at", DESCENDING)
            .skip(bounded_skip)
            .limit(bounded_limit)
        )
        items = await cursor.to_list(length=bounded_limit)
        return cast(list[dict[str, Any]], items), total

    async def mark_confirmed(
        self,
        sale_id: str,
        invoice_number: str,
    ) -> dict[str, Any] | None:
        return await self.update_status(
            sale_id,
            status_value="confirmed",
            timestamp_field="confirmed_at",
            extra_fields={"invoice_number": invoice_number},
        )

    async def mark_cancelled(self, sale_id: str) -> dict[str, Any] | None:
        return await self.update_status(
            sale_id,
            status_value="cancelled",
            timestamp_field="cancelled_at",
        )

    async def update_status(
        self,
        sale_id: str,
        status_value: str,
        timestamp_field: str,
        extra_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(sale_id):
            return None
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "status": status_value,
            timestamp_field: now,
            "updated_at": now,
        }
        if extra_fields:
            payload.update(extra_fields)
        updated = await self.collection.find_one_and_update(
            {"_id": ObjectId(sale_id)},
            {"$set": payload},
            return_document=ReturnDocument.AFTER,
        )
        return cast(dict[str, Any] | None, updated)


async def ensure_sale_indexes(db: AsyncIOMotorDatabase[Any]) -> None:
    repository = SaleRepository(db)
    await repository.create_indexes()
