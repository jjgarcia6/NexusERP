from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from auth.dependencies import require_role
from auth.schemas import RoleEnum, UserResponse
from sales.dependencies import get_point_of_sale, get_sale_service
from sales.schemas import SaleListResponse, SaleRequest, SaleResponse
from sales.services.sale_service import SaleService

router = APIRouter()


@router.post(
    "",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
@router.post(
    "/",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sale(
    sale: SaleRequest,
    service: Annotated[SaleService, Depends(get_sale_service)],
    user: Annotated[
        UserResponse,
        Depends(require_role(RoleEnum.admin, RoleEnum.vendedor)),
    ],
) -> SaleResponse:
    return await service.create_sale(sale, created_by=user.id)


@router.get(
    "",
    response_model=SaleListResponse,
    include_in_schema=False,
)
@router.get(
    "/",
    response_model=SaleListResponse,
)
async def list_sales(
    service: Annotated[SaleService, Depends(get_sale_service)],
    _: Annotated[
        UserResponse,
        Depends(require_role(RoleEnum.admin, RoleEnum.vendedor, RoleEnum.bodeguero)),
    ],
    status: str | None = Query(None),
    customer_id: str | None = Query(None),
    from_: str | None = Query(None, alias="from"),
    to: str | None = Query(None),
    skip: int = 0,
    limit: int = 50,
) -> SaleListResponse:
    return await service.list_sales(status, customer_id, from_, to, skip, limit)


@router.get(
    "/{id}",
    response_model=SaleResponse,
)
async def get_sale(
    id: str,
    service: Annotated[SaleService, Depends(get_sale_service)],
    _: Annotated[
        UserResponse,
        Depends(require_role(RoleEnum.admin, RoleEnum.vendedor, RoleEnum.bodeguero)),
    ],
) -> SaleResponse:
    return await service.get_sale(id)


@router.patch(
    "/{id}/confirm",
    response_model=SaleResponse,
)
async def confirm_sale(
    id: str,
    service: Annotated[SaleService, Depends(get_sale_service)],
    user: Annotated[
        UserResponse,
        Depends(require_role(RoleEnum.admin, RoleEnum.vendedor)),
    ],
    point_of_sale: Annotated[str, Depends(get_point_of_sale)],
) -> SaleResponse:
    return await service.confirm_sale(id, user.id, point_of_sale)


@router.patch("/{id}/cancel", response_model=SaleResponse)
async def cancel_sale(
    id: str,
    service: Annotated[SaleService, Depends(get_sale_service)],
    user: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
) -> SaleResponse:
    return await service.cancel_sale(id, user.id)
