import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import type { SalesReportType } from "../types/reports.types";

type SalesReportTableProps = {
  report: SalesReportType;
};

function formatMoney(value: number): string {
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

export function SalesReportTable({ report }: SalesReportTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Reporte de ventas</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Período</TableHead>
              <TableHead>Transacciones</TableHead>
              <TableHead>Subtotal</TableHead>
              <TableHead>IVA</TableHead>
              <TableHead>Total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {report.entries.map((entry) => (
              <TableRow key={entry.date}>
                <TableCell>{entry.date}</TableCell>
                <TableCell>{entry.transactions}</TableCell>
                <TableCell>{formatMoney(entry.subtotal_before_tax)}</TableCell>
                <TableCell>{formatMoney(entry.tax_amount)}</TableCell>
                <TableCell>{formatMoney(entry.total)}</TableCell>
              </TableRow>
            ))}
            <TableRow className="bg-slate-100 font-semibold dark:bg-slate-800">
              <TableCell>Total</TableCell>
              <TableCell>{report.total_transactions}</TableCell>
              <TableCell>-</TableCell>
              <TableCell>-</TableCell>
              <TableCell>{formatMoney(report.grand_total)}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
