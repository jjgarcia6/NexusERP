import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import type { PurchasesReportType } from "../types/reports.types";

type PurchasesReportTableProps = {
  report: PurchasesReportType;
};

function formatMoney(value: number): string {
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

function formatDate(date: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}

export function PurchasesReportTable({ report }: PurchasesReportTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Reporte de compras</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Proveedor</TableHead>
              <TableHead>Órdenes</TableHead>
              <TableHead>Total invertido</TableHead>
              <TableHead>Última orden</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {report.entries.map((entry, index) => (
              <TableRow key={`${entry.supplier_name}-${index}`}>
                <TableCell>{entry.supplier_name}</TableCell>
                <TableCell>{entry.total_orders}</TableCell>
                <TableCell>{formatMoney(entry.total_amount)}</TableCell>
                <TableCell>{formatDate(entry.last_order_at)}</TableCell>
              </TableRow>
            ))}
            <TableRow className="bg-slate-100 font-semibold dark:bg-slate-800">
              <TableCell>Total</TableCell>
              <TableCell>-</TableCell>
              <TableCell>{formatMoney(report.grand_total)}</TableCell>
              <TableCell>-</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
