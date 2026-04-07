from __future__ import annotations

from core.database import get_database
from reports.services.customer_report_service import CustomerReportService
from reports.services.dashboard_service import DashboardService
from reports.services.inventory_report_service import InventoryReportService
from reports.services.purchases_report_service import PurchasesReportService
from reports.services.sales_report_service import SalesReportService


def get_dashboard_service() -> DashboardService:
    return DashboardService(get_database())


def get_sales_report_service() -> SalesReportService:
    return SalesReportService(get_database())


def get_inventory_report_service() -> InventoryReportService:
    return InventoryReportService(get_database())


def get_customer_report_service() -> CustomerReportService:
    return CustomerReportService(get_database())


def get_purchases_report_service() -> PurchasesReportService:
    return PurchasesReportService(get_database())
