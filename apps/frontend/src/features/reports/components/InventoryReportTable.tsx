import { Badge } from "../../../components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { useAuth } from "../../auth";
import type { InventoryReportType } from "../types/reports.types";

type InventoryReportTableProps = {
  report: InventoryReportType;
};

function formatMoney(value: number): string {
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

export function InventoryReportTable({ report }: InventoryReportTableProps) {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Reporte de inventario</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Producto</TableHead>
              <TableHead>Disponible</TableHead>
              {isAdmin ? <TableHead>Costo</TableHead> : null}
              {isAdmin ? <TableHead>Valor</TableHead> : null}
              <TableHead>Vendidos</TableHead>
              <TableHead>Rotación</TableHead>
              <TableHead>Alerta</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {report.entries.map((entry) => (
              <TableRow key={entry.product_id}>
                <TableCell>{entry.product_name}</TableCell>
                <TableCell>{entry.available_quantity}</TableCell>
                {isAdmin ? <TableCell>{formatMoney(entry.unit_cost)}</TableCell> : null}
                {isAdmin ? <TableCell>{formatMoney(entry.total_value)}</TableCell> : null}
                <TableCell>{entry.units_sold}</TableCell>
                <TableCell>{entry.rotation_rate.toFixed(2)}</TableCell>
                <TableCell>
                  <Badge
                    className={entry.low_stock ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"}
                  >
                    {entry.low_stock ? "Stock bajo" : "Normal"}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
            <TableRow className="bg-slate-100 font-semibold dark:bg-slate-800">
              <TableCell>Total inventario</TableCell>
              <TableCell>-</TableCell>
              {isAdmin ? <TableCell>-</TableCell> : null}
              {isAdmin ? <TableCell>{formatMoney(report.grand_total_value)}</TableCell> : null}
              <TableCell>-</TableCell>
              <TableCell>-</TableCell>
              <TableCell>-</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
