import { useEffect, useState } from "react";
import { DollarSign, Receipt, ShoppingCart } from "lucide-react";

import { LowStockPanel } from "../features/inventory";
import {
  DashboardKPICard,
  DashboardTopLists,
  PeriodSelector,
  SalesChart,
  useDashboard,
  useReports,
  type SalesReportType,
  type PeriodRange,
} from "../features/reports";

export function DashboardPage() {
  const now = new Date();
  const [period, setPeriod] = useState<PeriodRange>({
    from: new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 0, 0, 0)).toISOString(),
    to: new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 23, 59, 59, 999)).toISOString(),
  });

  const { dashboard, isLoading, isError } = useDashboard({ period });
  const salesReport = useReports({ type: "sales", period, granularity: "day" });
  const salesEntries = (salesReport.data as SalesReportType | null)?.entries ?? [];

  useEffect(() => {
    document.title = "NexusERP — Dashboard";
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
      <section className="mx-auto w-full max-w-7xl space-y-4">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <PeriodSelector value={period} onChange={setPeriod} />
        </header>

        {isError ? <p className="text-sm text-red-600">No se pudo cargar el dashboard.</p> : null}

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {isLoading || !dashboard ? (
            <>
              <div className="h-28 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800" />
              <div className="h-28 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800" />
              <div className="h-28 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800" />
            </>
          ) : (
            <>
              <DashboardKPICard
                label="Total ventas"
                value={dashboard.total_sales_amount}
                unit="currency"
                icon={DollarSign}
              />
              <DashboardKPICard
                label="Transacciones"
                value={dashboard.total_transactions}
                unit="number"
                icon={ShoppingCart}
              />
              <DashboardKPICard
                label="Ticket promedio"
                value={dashboard.average_ticket}
                unit="currency"
                icon={Receipt}
              />
            </>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <SalesChart entries={salesEntries} />
          </div>
          <div>
            <LowStockPanel />
          </div>
        </div>

        <DashboardTopLists
          topProducts={dashboard?.top_products ?? []}
          topCustomers={dashboard?.top_customers ?? []}
        />
      </section>
    </main>
  );
}
