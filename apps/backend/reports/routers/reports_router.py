from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from auth.dependencies import require_role
from auth.schemas import RoleEnum, UserResponse
from reports.dependencies import (
    get_customer_report_service,
    get_dashboard_service,
    get_inventory_report_service,
    get_purchases_report_service,
    get_sales_report_service,
)
from reports.schemas import (
    CustomerReportResponse,
    DashboardResponse,
    GranularityEnum,
    InventoryReportResponse,
    PurchasesReportResponse,
    SalesReportResponse,
)
from reports.services.customer_report_service import CustomerReportService
from reports.services.dashboard_service import DashboardService
from reports.services.inventory_report_service import InventoryReportService
from reports.services.purchases_report_service import PurchasesReportService
from reports.services.sales_report_service import SalesReportService
from reports.utils.period import get_default_period, parse_period

router = APIRouter()


def _resolve_period(from_: str | None, to: str | None) -> tuple[datetime, datetime]:
    if from_ is None and to is None:
        return get_default_period()

    if from_ is None or to is None:
        raise HTTPException(status_code=422, detail="Debe enviar ambos parametros: from y to.")

    return parse_period(from_, to)


@router.get("", response_model=DashboardResponse, include_in_schema=False)
@router.get("/", response_model=DashboardResponse)
async def get_dashboard_summary(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
    user: Annotated[
        UserResponse,
        Depends(require_role(RoleEnum.admin, RoleEnum.vendedor)),
    ],
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = Query(default=None),
) -> DashboardResponse:
    from_date, to_date = _resolve_period(from_, to)
    return await service.get_dashboard_summary(
        from_date=from_date,
        to_date=to_date,
        role=user.role,
        user_id=user.id,
    )


@router.get("/sales", response_model=SalesReportResponse)
async def get_sales_report(
    service: Annotated[SalesReportService, Depends(get_sales_report_service)],
    user: Annotated[
        UserResponse,
        Depends(require_role(RoleEnum.admin, RoleEnum.vendedor)),
    ],
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = Query(default=None),
    granularity: GranularityEnum = GranularityEnum.day,
) -> SalesReportResponse:
    from_date, to_date = _resolve_period(from_, to)
    return await service.get_sales_report(
        from_date=from_date,
        to_date=to_date,
        granularity=granularity,
        role=user.role,
        user_id=user.id,
    )


@router.get("/inventory", response_model=InventoryReportResponse)
async def get_inventory_report(
    service: Annotated[InventoryReportService, Depends(get_inventory_report_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = Query(default=None),
) -> InventoryReportResponse:
    if (from_ is None) != (to is None):
        raise HTTPException(status_code=422, detail="Debe enviar ambos parametros: from y to.")

    from_date = None
    to_date = None
    if from_ is not None and to is not None:
        from_date, to_date = parse_period(from_, to)

    return await service.get_inventory_report(from_date=from_date, to_date=to_date)


@router.get("/customers", response_model=CustomerReportResponse)
async def get_customer_report(
    service: Annotated[CustomerReportService, Depends(get_customer_report_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> CustomerReportResponse:
    from_date, to_date = _resolve_period(from_, to)
    return await service.get_customer_report(from_date=from_date, to_date=to_date, limit=limit)


@router.get("/purchases", response_model=PurchasesReportResponse)
async def get_purchases_report(
    service: Annotated[PurchasesReportService, Depends(get_purchases_report_service)],
    _: Annotated[UserResponse, Depends(require_role(RoleEnum.admin))],
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = Query(default=None),
) -> PurchasesReportResponse:
    from_date, to_date = _resolve_period(from_, to)
    return await service.get_purchases_report(from_date=from_date, to_date=to_date)
