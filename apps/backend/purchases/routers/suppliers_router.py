from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from auth.dependencies import require_role
from auth.schemas import RoleEnum, UserResponse
from purchases.dependencies import get_supplier_service
from purchases.schemas import SupplierRequest, SupplierResponse, SupplierUpdateRequest
from purchases.services.supplier_service import SupplierService

router = APIRouter()


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: SupplierRequest,
    service: Annotated[SupplierService, Depends(get_supplier_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> SupplierResponse:
    return await service.create_supplier(payload)


@router.get("", response_model=list[SupplierResponse])
async def list_suppliers(
    service: Annotated[SupplierService, Depends(get_supplier_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin, RoleEnum.bodeguero))],
) -> list[SupplierResponse]:
    return await service.list_suppliers()


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    service: Annotated[SupplierService, Depends(get_supplier_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin, RoleEnum.bodeguero))],
) -> SupplierResponse:
    return await service.get_supplier(supplier_id)


@router.patch("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    payload: SupplierUpdateRequest,
    service: Annotated[SupplierService, Depends(get_supplier_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> SupplierResponse:
    return await service.update_supplier(supplier_id, payload)
