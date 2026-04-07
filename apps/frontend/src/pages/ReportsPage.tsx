import { useEffect, useState } from "react";

import { Button } from "../components/ui/button";
import { Select } from "../components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { useAuth } from "../features/auth";
import {
  CustomerReportTable,
  InventoryReportTable,
  PeriodSelector,
  PurchasesReportTable,
  SalesReportTable,
  useReports,
  type PeriodRange,
} from "../features/reports";
import type {
  CustomerReportType,
  GranularityType,
  InventoryReportType,
  PurchasesReportType,
  SalesReportType,
} from "../features/reports/types/reports.types";

const now = new Date();
const defaultPeriod: PeriodRange = {
  from: new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 0, 0, 0)).toISOString(),
  to: new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 23, 59, 59, 999)).toISOString(),
};

export function ReportsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<"sales" | "inventory" | "customers" | "purchases">("sales");
  const [period, setPeriod] = useState<PeriodRange>(defaultPeriod);
  const [granularity, setGranularity] = useState<GranularityType>("day");

  const { data, isLoading, isError } = useReports({
    type: activeTab,
    period,
    granularity,
  });

  useEffect(() => {
    document.title = "NexusERP — Reportes";
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
      <section className="mx-auto w-full max-w-7xl space-y-4">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold">Reportes</h1>
          <PeriodSelector value={period} onChange={setPeriod} />
        </header>

        <Tabs defaultValue="sales" className="space-y-4">
          <TabsList>
            <TabsTrigger value="sales" onClick={() => setActiveTab("sales")}>Ventas</TabsTrigger>
            {user?.role === "admin" ? (
              <TabsTrigger value="inventory" onClick={() => setActiveTab("inventory")}>Inventario</TabsTrigger>
            ) : null}
            {user?.role === "admin" ? (
              <TabsTrigger value="customers" onClick={() => setActiveTab("customers")}>Clientes</TabsTrigger>
            ) : null}
            {user?.role === "admin" ? (
              <TabsTrigger value="purchases" onClick={() => setActiveTab("purchases")}>Compras</TabsTrigger>
            ) : null}
          </TabsList>

          <div className="flex items-center justify-between gap-2">
            {activeTab === "sales" ? (
              <Select
                value={granularity}
                onChange={(event) => setGranularity(event.target.value as GranularityType)}
                className="w-40"
              >
                <option value="day">Día</option>
                <option value="week">Semana</option>
                <option value="month">Mes</option>
              </Select>
            ) : <div />}

            <Button type="button" onClick={() => window.print()}>
              Imprimir
            </Button>
          </div>

          {isLoading ? <p>Cargando reporte...</p> : null}
          {isError ? <p className="text-red-600">No se pudo cargar el reporte.</p> : null}

          <TabsContent value="sales">
            {activeTab === "sales" && data ? (
              <SalesReportTable report={data as SalesReportType} />
            ) : null}
          </TabsContent>

          <TabsContent value="inventory">
            {activeTab === "inventory" && data ? (
              <InventoryReportTable report={data as InventoryReportType} />
            ) : null}
          </TabsContent>

          <TabsContent value="customers">
            {activeTab === "customers" && data ? (
              <CustomerReportTable report={data as CustomerReportType} />
            ) : null}
          </TabsContent>

          <TabsContent value="purchases">
            {activeTab === "purchases" && data ? (
              <PurchasesReportTable report={data as PurchasesReportType} />
            ) : null}
          </TabsContent>
        </Tabs>
      </section>
    </main>
  );
}
