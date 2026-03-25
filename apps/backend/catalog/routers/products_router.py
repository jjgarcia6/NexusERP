from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from auth.dependencies import get_current_user, require_role
from auth.schemas import RoleEnum, UserResponse
from catalog.dependencies import get_product_service
from catalog.schemas import (
    ProductListResponse,
    ProductRequest,
    ProductResponse,
    ProductUpdateRequest,
)
from catalog.services.product_service import ProductService

router = APIRouter()


def _serialize_product_for_role(product: dict[str, Any], role: RoleEnum) -> ProductResponse:
    return ProductResponse.model_validate(product, context={"role": role.value})


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductRequest,
    service: Annotated[ProductService, Depends(get_product_service)],
    current_user: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> ProductResponse:
    product = await service.create_product(payload, created_by=current_user.id)
    return _serialize_product_for_role(product, current_user.role)


@router.get("", response_model=ProductListResponse)
async def list_products(
    service: Annotated[ProductService, Depends(get_product_service)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    search: str | None = None,
    category_id: str | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ProductListResponse:
    products, total = await service.list_products(
        search=search,
        category_id=category_id,
        skip=skip,
        limit=limit,
    )
    serialized_items = [
        _serialize_product_for_role(product, current_user.role) for product in products
    ]
    return ProductListResponse(
        items=serialized_items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    service: Annotated[ProductService, Depends(get_product_service)],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> ProductResponse:
    product = await service.get_product(product_id)
    return _serialize_product_for_role(product, current_user.role)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    payload: ProductUpdateRequest,
    service: Annotated[ProductService, Depends(get_product_service)],
    current_user: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> ProductResponse:
    product = await service.update_product(product_id, payload)
    return _serialize_product_for_role(product, current_user.role)
