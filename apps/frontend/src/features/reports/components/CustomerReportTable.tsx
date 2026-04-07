import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import type { CustomerReportType } from "../types/reports.types";

type CustomerReportTableProps = {
  report: CustomerReportType;
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

export function CustomerReportTable({ report }: CustomerReportTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Reporte de clientes</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Posición</TableHead>
              <TableHead>Cliente</TableHead>
              <TableHead>Identificación</TableHead>
              <TableHead>Compras</TableHead>
              <TableHead>Total</TableHead>
              <TableHead>Última compra</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {report.entries.map((entry, index) => (
              <TableRow key={`${entry.customer_name}-${index}`}>
                <TableCell>{index + 1}</TableCell>
                <TableCell>{entry.customer_name}</TableCell>
                <TableCell>{entry.identification_masked}</TableCell>
                <TableCell>{entry.total_purchases}</TableCell>
                <TableCell>{formatMoney(entry.total_amount)}</TableCell>
                <TableCell>{formatDate(entry.last_purchase_at)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
