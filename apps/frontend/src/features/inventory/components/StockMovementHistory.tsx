import { useMemo, useState } from "react";

import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select } from "../../../components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { useAuth } from "../../auth";
import { useStockLevels } from "../hooks/useStockLevels";
import { useStockMovements } from "../hooks/useStockMovements";
import { movementTypeSchema } from "../types/inventory.types";

const PAGE_SIZE = 20;

export function StockMovementHistory() {
  const { user } = useAuth();
  const [productId, setProductId] = useState<string>("");
  const [movementType, setMovementType] = useState<string>("");
  const [fromDate, setFromDate] = useState<string>("");
  const [toDate, setToDate] = useState<string>("");
  const [skip, setSkip] = useState(0);

  const { stockLevels, isLoading: levelsLoading } = useStockLevels({ skip: 0, limit: 100 });
  const { movements, total, isLoading } = useStockMovements({
    product_id: productId || undefined,
    type: movementType || undefined,
    from: fromDate || undefined,
    to: toDate || undefined,
    skip,
    limit: PAGE_SIZE,
  });

  const canView = user?.role === "admin" || user?.role === "bodeguero";

  const typeClass = useMemo(
    () => ({
      purchase_entry: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
      manual_entry: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
      sale_exit: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
      manual_exit: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
      adjustment: "bg-slate-200 text-slate-900 dark:bg-slate-700 dark:text-slate-100",
    }),
    [],
  );

  if (!canView) {
    return null;
  }

  return (
    <section className="space-y-4 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <header>
        <h2 className="text-2xl font-semibold tracking-tight">Historial de movimientos</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">Consulta movimientos con filtros por producto, tipo y fechas.</p>
      </header>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <Label className="flex flex-col gap-2">
          Producto
          <Select value={productId} disabled={levelsLoading} onChange={(event) => { setProductId(event.target.value); setSkip(0); }}>
            <option value="">Todos</option>
            {stockLevels.map((item) => (
              <option key={item.product_id} value={item.product_id}>{item.product_name}</option>
            ))}
          </Select>
        </Label>

        <Label className="flex flex-col gap-2">
          Tipo
          <Select value={movementType} onChange={(event) => { setMovementType(event.target.value); setSkip(0); }}>
            <option value="">Todos</option>
            {movementTypeSchema.options.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </Select>
        </Label>

        <Label className="flex flex-col gap-2">
          Desde
          <Input type="date" value={fromDate} onChange={(event) => { setFromDate(event.target.value); setSkip(0); }} />
        </Label>

        <Label className="flex flex-col gap-2">
          Hasta
          <Input type="date" value={toDate} onChange={(event) => { setToDate(event.target.value); setSkip(0); }} />
        </Label>
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-600 dark:text-slate-300">Cargando movimientos...</p>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Fecha</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Producto</TableHead>
                <TableHead>Antes</TableHead>
                <TableHead>Cantidad</TableHead>
                <TableHead>Después</TableHead>
                <TableHead>Motivo</TableHead>
                <TableHead>Referencia</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {movements.map((movement) => (
                <TableRow key={movement.id}>
                  <TableCell>{new Date(movement.created_at).toLocaleString("es-EC")}</TableCell>
                  <TableCell>
                    <span className={`rounded px-2 py-1 text-xs font-medium ${typeClass[movement.type]}`}>
                      {movement.type}
                    </span>
                  </TableCell>
                  <TableCell>{movement.product_name}</TableCell>
                  <TableCell>{movement.quantity_before}</TableCell>
                  <TableCell>{movement.quantity}</TableCell>
                  <TableCell>{movement.quantity_after}</TableCell>
                  <TableCell>{movement.reason ?? "-"}</TableCell>
                  <TableCell>{movement.reference_id ?? "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="flex items-center justify-end gap-2">
            <Button
              type="button"
              className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
              disabled={skip === 0}
              onClick={() => setSkip((previous) => Math.max(previous - PAGE_SIZE, 0))}
            >
              Anterior
            </Button>
            <Button type="button" disabled={skip + PAGE_SIZE >= total} onClick={() => setSkip((previous) => previous + PAGE_SIZE)}>
              Siguiente
            </Button>
          </div>
        </>
      )}
    </section>
  );
}
