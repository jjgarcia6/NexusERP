from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from auth.dependencies import require_role
from auth.schemas import RoleEnum, UserResponse
from purchases.dependencies import get_purchase_order_service
from purchases.schemas import (
    OrderStatusEnum,
    PurchaseOrderListResponse,
    PurchaseOrderRequest,
    PurchaseOrderResponse,
)
from purchases.services.purchase_order_service import PurchaseOrderService

router = APIRouter()


@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: PurchaseOrderRequest,
    service: Annotated[PurchaseOrderService, Depends(get_purchase_order_service)],
    current_user: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> PurchaseOrderResponse:
    return await service.create_order(payload, created_by=current_user.id)


@router.get("", response_model=PurchaseOrderListResponse)
async def list_orders(
    service: Annotated[PurchaseOrderService, Depends(get_purchase_order_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin, RoleEnum.bodeguero))],
    order_status: Annotated[OrderStatusEnum | None, Query(alias="status")] = None,
    supplier_id: str | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PurchaseOrderListResponse:
    return await service.list_orders(
        order_status=order_status,
        supplier_id=supplier_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{order_id}", response_model=PurchaseOrderResponse)
async def get_order(
    order_id: str,
    service: Annotated[PurchaseOrderService, Depends(get_purchase_order_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin, RoleEnum.bodeguero))],
) -> PurchaseOrderResponse:
    return await service.get_order(order_id)


@router.patch("/{order_id}/confirm", response_model=PurchaseOrderResponse)
async def confirm_order(
    order_id: str,
    service: Annotated[PurchaseOrderService, Depends(get_purchase_order_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> PurchaseOrderResponse:
    return await service.confirm_order(order_id)


@router.patch("/{order_id}/receive", response_model=PurchaseOrderResponse)
async def receive_order(
    order_id: str,
    service: Annotated[PurchaseOrderService, Depends(get_purchase_order_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin, RoleEnum.bodeguero))],
) -> PurchaseOrderResponse:
    return await service.receive_order(order_id)


@router.patch("/{order_id}/cancel", response_model=PurchaseOrderResponse)
async def cancel_order(
    order_id: str,
    service: Annotated[PurchaseOrderService, Depends(get_purchase_order_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> PurchaseOrderResponse:
    return await service.cancel_order(order_id)
