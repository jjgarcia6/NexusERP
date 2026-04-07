from __future__ import annotations

from typing import Any

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from auth.schemas import RoleEnum
from customers.repositories.customer_repository import CustomerRepository
from customers.schemas import (
    CustomerRequest,
    CustomerSearchResult,
    CustomerTypeEnum,
    CustomerUpdateRequest,
)


class CustomerService:
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    async def create_customer(self, payload: CustomerRequest, *, created_by: str) -> dict[str, Any]:
        existing = await self.customer_repository.find_by_identification(
            payload.identification_number
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un cliente con ese numero de identificacion",
            )

        to_insert = payload.model_dump(mode="json")
        to_insert["created_by"] = (
            ObjectId(created_by) if ObjectId.is_valid(created_by) else created_by
        )

        try:
            created = await self.customer_repository.create_customer(to_insert)
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un cliente con ese numero de identificacion",
            ) from exc

        return self._to_customer_dict(created)

    async def list_customers(
        self,
        *,
        search: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[dict[str, Any]], int]:
        items, total = await self.customer_repository.find_all(
            search=search,
            skip=skip,
            limit=limit,
        )
        return [self._to_customer_dict(item) for item in items], total

    async def search_customers(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        items = await self.customer_repository.search_quick(query, limit=limit)
        return [self._to_search_result_dict(item) for item in items]

    async def get_customer(self, customer_id: str) -> dict[str, Any]:
        customer = await self.customer_repository.find_by_id(customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        return self._to_customer_dict(customer)

    async def update_customer(
        self,
        customer_id: str,
        payload: CustomerUpdateRequest,
        *,
        actor_role: RoleEnum,
    ) -> dict[str, Any]:
        customer = await self.customer_repository.find_by_id(customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )

        updates = payload.model_dump(exclude_none=True)
        if not updates:
            return self._to_customer_dict(customer)

        if (
            "is_active" in updates
            and updates["is_active"] is False
            and actor_role != RoleEnum.admin
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo un administrador puede desactivar clientes",
            )

        if updates.get("is_active") is False:
            return await self.deactivate_customer(customer_id)

        updated = await self.customer_repository.update_customer(customer_id, updates)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        return self._to_customer_dict(updated)

    async def deactivate_customer(self, customer_id: str) -> dict[str, Any]:
        updated = await self.customer_repository.update_customer(
            customer_id,
            {"is_active": False},
        )
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        return self._to_customer_dict(updated)

    from enum import Enum
    from typing import Any
    def _to_customer_dict(self, document: dict[str, Any]) -> dict[str, Any]:
        raw_customer_type = document.get("customer_type")
        # Normaliza el valor para que siempre sea el valor del Enum
        # Limpieza robusta: si el valor contiene 'persona_natural' o 'juridica', lo normaliza
        customer_type = str(raw_customer_type or "")
        if "persona_natural" in customer_type:
            customer_type = "persona_natural"
        elif "juridica" in customer_type:
            customer_type = "juridica"
        else:
            # Si no es ninguno, deja el valor tal cual para que Pydantic lo rechace explícitamente
            pass

        return {
            "id": str(document.get("_id")),
            "name": str(document.get("name") or ""),
            "customer_type": customer_type,
            "identification_number": str(document.get("identification_number") or ""),
            "email": str(document["email"]) if document.get("email") else None,
            "phone": str(document["phone"]) if document.get("phone") else None,
            "address": str(document["address"]) if document.get("address") else None,
            "is_active": bool(document.get("is_active", False)),
            "created_at": document.get("created_at").isoformat() if document.get("created_at") else None,
            "updated_at": document.get("updated_at").isoformat() if document.get("updated_at") else None,
        }

    def _to_search_result_dict(self, document: dict[str, Any]) -> dict[str, Any]:
        raw_customer_type = document.get("customer_type")
        customer_type = (
            raw_customer_type
            if isinstance(raw_customer_type, CustomerTypeEnum)
            else CustomerTypeEnum(str(raw_customer_type))
        )

        parsed = CustomerSearchResult(
            id=str(document.get("_id")),
            name=str(document.get("name") or ""),
            identification_number=str(document.get("identification_number") or ""),
            customer_type=customer_type,
        )
        return parsed.model_dump()
