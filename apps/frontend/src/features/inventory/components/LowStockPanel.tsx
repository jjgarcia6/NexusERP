import { Card } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { useStockLevels } from "../hooks/useStockLevels";

export function LowStockPanel() {
  const { stockLevels, isLoading } = useStockLevels({ low_stock: true, skip: 0, limit: 100 });

  return (
    <Card className="space-y-4 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <header>
        <h3 className="text-lg font-semibold tracking-tight">Alertas de stock bajo</h3>
        <p className="text-sm text-slate-600 dark:text-slate-300">Productos críticos para reabastecimiento.</p>
      </header>

      {isLoading ? <p className="text-sm text-slate-600 dark:text-slate-300">Cargando alertas...</p> : null}

      {!isLoading && stockLevels.length === 0 ? (
        <p className="text-sm text-slate-600 dark:text-slate-300">Todo el inventario está en niveles adecuados</p>
      ) : null}

      <div className="space-y-3">
        {stockLevels.map((item) => (
          <div key={item.product_id} className="rounded-lg border border-slate-300 p-3 dark:border-slate-700">
            <p className="font-medium">{item.product_name}</p>
            <p className="text-sm text-slate-600 dark:text-slate-300">Disponible: {item.available_quantity}</p>
            <p className="text-sm text-slate-600 dark:text-slate-300">Mínimo: {item.min_stock}</p>
            <p className="text-sm text-slate-600 dark:text-slate-300">Diferencia: {item.available_quantity - item.min_stock}</p>
            <Button type="button" className="mt-3" onClick={() => (window.location.href = "/purchases")}>Crear orden de compra</Button>
          </div>
        ))}
      </div>
    </Card>
  );
}
