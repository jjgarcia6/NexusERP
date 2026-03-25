import { useEffect } from "react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { useAuth } from "../features/auth";
import { LowStockPanel, StockMovementHistory, StockTable } from "../features/inventory";

export function InventoryPage() {
  const { user } = useAuth();

  useEffect(() => {
    document.title = "NexusERP — Inventario";
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
      <section className="mx-auto w-full max-w-6xl space-y-4">
        <Tabs defaultValue="stock" className="space-y-4">
          <TabsList>
            <TabsTrigger value="stock">Stock actual</TabsTrigger>
            {(user?.role === "admin" || user?.role === "bodeguero") ? (
              <TabsTrigger value="movements">Movimientos</TabsTrigger>
            ) : null}
          </TabsList>

          <TabsContent value="stock">
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <StockTable />
              </div>
              <div>
                <LowStockPanel />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="movements">
            <StockMovementHistory />
          </TabsContent>
        </Tabs>
      </section>
    </main>
  );
}
