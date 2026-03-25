from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from auth.dependencies import get_current_user, require_role
from auth.schemas import RoleEnum, UserResponse
from inventory.dependencies import get_inventory_service
from inventory.schemas import (
    MovementTypeEnum,
    StockInitRequest,
    StockLevelResponse,
    StockListResponse,
    StockMovementListResponse,
    StockMovementRequest,
    StockMovementResponse,
)
from inventory.services.inventory_service import InventoryService

router = APIRouter()


@router.post(
    "/stock/{product_id}/initialize",
    response_model=StockLevelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def initialize_stock(
    product_id: Annotated[str, Path(min_length=1)],
    payload: StockInitRequest,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    current_user: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> StockLevelResponse:
    data = await service.initialize_stock(
        product_id=product_id,
        quantity=payload.quantity,
        min_stock=payload.min_stock,
        user_id=current_user.id,
    )
    return StockLevelResponse.model_validate(data)


@router.get("/stock", response_model=StockListResponse)
async def list_stock(
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    _: Annotated[UserResponse, Depends(get_current_user)],
    low_stock: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> StockListResponse:
    items, total = await service.list_stock_levels(
        low_stock=low_stock,
        skip=skip,
        limit=limit,
    )
    serialized_items = [StockLevelResponse.model_validate(item) for item in items]
    return StockListResponse(items=serialized_items, total=total, skip=skip, limit=limit)


@router.get("/stock/{product_id}", response_model=StockLevelResponse)
async def get_stock_by_product(
    product_id: Annotated[str, Path(min_length=1)],
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    _: Annotated[UserResponse, Depends(get_current_user)],
) -> StockLevelResponse:
    data = await service.get_stock_level(product_id)
    return StockLevelResponse.model_validate(data)


@router.post(
    "/movements",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_movement(
    payload: StockMovementRequest,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    current_user: Annotated[
        UserResponse,
        Depends(require_role(RoleEnum.admin, RoleEnum.bodeguero)),
    ],
) -> StockMovementResponse:
    movement = await service.register_movement(payload, current_user.id)
    return StockMovementResponse.model_validate(movement)


@router.get("/movements", response_model=StockMovementListResponse)
async def list_movements(
    service: Annotated[InventoryService, Depends(get_inventory_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin, RoleEnum.bodeguero))],
    product_id: str | None = None,
    type: MovementTypeEnum | None = None,
    from_date: Annotated[datetime | None, Query(alias="from")] = None,
    to_date: Annotated[datetime | None, Query(alias="to")] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> StockMovementListResponse:
    items, total = await service.list_movements(
        product_id=product_id,
        movement_type=type.value if type else None,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit,
    )
    serialized_items = [StockMovementResponse.model_validate(item) for item in items]
    return StockMovementListResponse(
        items=serialized_items,
        total=total,
        skip=skip,
        limit=limit,
    )
