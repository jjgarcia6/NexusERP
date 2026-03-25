from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from purchases.repositories.supplier_repository import SupplierRepository
from purchases.schemas import SupplierRequest, SupplierResponse, SupplierUpdateRequest


def _to_supplier_response(document: dict[str, Any]) -> SupplierResponse:
    created_at = document.get("created_at")
    updated_at = document.get("updated_at")
    if not isinstance(created_at, datetime) or not isinstance(updated_at, datetime):
        raise TypeError("Invalid supplier date fields")

    return SupplierResponse(
        id=str(document["_id"]),
        name=str(document["name"]),
        ruc=(str(document["ruc"]) if document.get("ruc") else None),
        contact_name=(str(document["contact_name"]) if document.get("contact_name") else None),
        contact_email=(str(document["contact_email"]) if document.get("contact_email") else None),
        contact_phone=(str(document["contact_phone"]) if document.get("contact_phone") else None),
        address=(str(document["address"]) if document.get("address") else None),
        is_active=bool(document["is_active"]),
        created_at=created_at,
        updated_at=updated_at,
    )


class SupplierService:
    def __init__(self, supplier_repository: SupplierRepository) -> None:
        self.supplier_repository = supplier_repository

    async def create_supplier(self, payload: SupplierRequest) -> SupplierResponse:
        if payload.ruc:
            existing_ruc = await self.supplier_repository.find_by_ruc(payload.ruc)
            if existing_ruc is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un proveedor con ese RUC",
                )

        if payload.contact_email:
            existing_email = await self.supplier_repository.find_by_email(payload.contact_email)
            if existing_email is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un proveedor con ese email",
                )

        try:
            created = await self.supplier_repository.create_supplier(payload.model_dump())
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Proveedor duplicado"
            ) from exc

        return _to_supplier_response(created)

    async def list_suppliers(self) -> list[SupplierResponse]:
        suppliers = await self.supplier_repository.find_all()
        return [_to_supplier_response(item) for item in suppliers]

    async def get_supplier(self, supplier_id: str) -> SupplierResponse:
        supplier = await self.supplier_repository.find_by_id(supplier_id, include_inactive=True)
        if supplier is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado"
            )
        return _to_supplier_response(supplier)

    async def update_supplier(
        self, supplier_id: str, payload: SupplierUpdateRequest
    ) -> SupplierResponse:
        current = await self.supplier_repository.find_by_id(supplier_id, include_inactive=True)
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado"
            )

        updates = payload.model_dump(exclude_none=True)
        if not updates:
            return _to_supplier_response(current)

        if "ruc" in updates and updates["ruc"]:
            next_ruc = str(updates["ruc"])
            existing_ruc = await self.supplier_repository.find_by_ruc(next_ruc)
            if existing_ruc is not None and str(existing_ruc["_id"]) != supplier_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un proveedor con ese RUC",
                )

        if "contact_email" in updates and updates["contact_email"]:
            next_email = str(updates["contact_email"])
            existing_email = await self.supplier_repository.find_by_email(next_email)
            if existing_email is not None and str(existing_email["_id"]) != supplier_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un proveedor con ese email",
                )

        try:
            updated = await self.supplier_repository.update_supplier(supplier_id, updates)
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Proveedor duplicado"
            ) from exc

        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado"
            )
        return _to_supplier_response(updated)

    async def deactivate_supplier(self, supplier_id: str) -> SupplierResponse:
        updated = await self.supplier_repository.update_supplier(supplier_id, {"is_active": False})
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado"
            )
        return _to_supplier_response(updated)
