from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.dependencies import require_role
from auth.schemas import RoleEnum, UserResponse
from customers.dependencies import get_customer_service
from customers.schemas import (
    CustomerListResponse,
    CustomerRequest,
    CustomerResponse,
    CustomerSearchResult,
    CustomerUpdateRequest,
)
from customers.services.customer_service import CustomerService

router = APIRouter()


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerRequest,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[
        UserResponse,
        Depends(require_role(RoleEnum.admin, RoleEnum.vendedor)),
    ],
) -> CustomerResponse:
    created = await service.create_customer(payload, created_by=current_user.id)
    return CustomerResponse.model_validate(created)


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    service: Annotated[CustomerService, Depends(get_customer_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin, RoleEnum.vendedor))],
    search: str | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> CustomerListResponse:
    items, total = await service.list_customers(search=search, skip=skip, limit=limit)
    serialized_items = [CustomerResponse.model_validate(item) for item in items]
    return CustomerListResponse(items=serialized_items, total=total, skip=skip, limit=limit)


@router.get("/search", response_model=list[CustomerSearchResult])
async def search_customers(
    service: Annotated[CustomerService, Depends(get_customer_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin, RoleEnum.vendedor))],
    q: str = Query(default=""),
) -> list[CustomerSearchResult]:
    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El termino de busqueda debe tener al menos 2 caracteres",
        )

    items = await service.search_customers(q.strip(), limit=10)
    return [CustomerSearchResult.model_validate(item) for item in items]


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin, RoleEnum.vendedor))],
) -> CustomerResponse:
    customer = await service.get_customer(customer_id)
    return CustomerResponse.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    payload: CustomerUpdateRequest,
    service: Annotated[CustomerService, Depends(get_customer_service)],
    current_user: Annotated[
        UserResponse,
        Depends(require_role(RoleEnum.admin, RoleEnum.vendedor)),
    ],
) -> CustomerResponse:
    customer = await service.update_customer(
        customer_id,
        payload,
        actor_role=current_user.role,
    )
    return CustomerResponse.model_validate(customer)
