import { useState } from "react";

import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import type { RoleType } from "../../auth";
import { useSales } from "../hooks/useSales";
import type { SaleStatusType, SaleType } from "../types/sales.types";

type SaleDetailProps = {
  sale: SaleType;
  role?: RoleType;
  onCancelled?: (updatedSale: SaleType) => void;
};

function formatMoney(value: number): string {
  return `$${value.toFixed(2)}`;
}

function formatDate(value: string | null): string {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString("es-EC");
}

function statusLabel(status: SaleStatusType): string {
  if (status === "draft") {
    return "Borrador";
  }
  if (status === "confirmed") {
    return "Confirmada";
  }
  return "Cancelada";
}

function statusClassName(status: SaleStatusType): string {
  if (status === "confirmed") {
    return "bg-green-200 text-green-900 dark:bg-green-800 dark:text-green-100";
  }
  if (status === "cancelled") {
    return "bg-red-200 text-red-900 dark:bg-red-800 dark:text-red-100";
  }
  return "bg-slate-300 text-slate-900 dark:bg-slate-700 dark:text-slate-100";
}

export function SaleDetail({ sale, role, onCancelled }: SaleDetailProps) {
  const { cancelSale } = useSales();
  const [isCancelling, setIsCancelling] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const canCancel = role === "admin" && sale.status === "confirmed";

  async function handleCancelSale() {
    setIsCancelling(true);
    setErrorMessage(null);

    try {
      const updatedSale = await cancelSale(sale.id);
      onCancelled?.(updatedSale);
    } catch {
      setErrorMessage("No fue posible cancelar la venta.");
    } finally {
      setIsCancelling(false);
    }
  }

  return (
    <>
      <style>
        {`@media print {
          .no-print { display: none !important; }
          .print-area { width: 210mm; margin: 0 auto; box-shadow: none !important; border: 0 !important; }
          body { background: white !important; }
        }`}
      </style>

      <Card className="print-area">
        <CardHeader className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="space-y-1">
            <CardTitle>Comprobante #{sale.invoice_number ?? "PENDIENTE"}</CardTitle>
            <p className="text-sm text-slate-600 dark:text-slate-300">Cliente: {sale.customer_name}</p>
            <p className="text-sm text-slate-600 dark:text-slate-300">Identificación: {sale.customer_identification}</p>
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Confirmación: {formatDate(sale.confirmed_at)}
            </p>
          </div>
          <Badge className={statusClassName(sale.status)}>{statusLabel(sale.status)}</Badge>
        </CardHeader>

        <CardContent className="space-y-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Producto</TableHead>
                <TableHead>Cantidad</TableHead>
                <TableHead>Precio unitario</TableHead>
                <TableHead>Subtotal</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sale.lines.map((line) => (
                <TableRow key={`${line.product_id}-${line.product_name}`}>
                  <TableCell className="font-medium">{line.product_name}</TableCell>
                  <TableCell>{line.quantity}</TableCell>
                  <TableCell>{formatMoney(line.unit_price)}</TableCell>
                  <TableCell>{formatMoney(line.subtotal)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="space-y-1 border-t border-slate-200 pt-3 text-sm dark:border-slate-700">
            <div className="flex items-center justify-between">
              <span>Subtotal</span>
              <span>{formatMoney(sale.subtotal_before_tax)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>IVA (12%)</span>
              <span>{formatMoney(sale.tax_amount)}</span>
            </div>
            <div className="flex items-center justify-between text-base font-semibold">
              <span>Total</span>
              <span>{formatMoney(sale.total)}</span>
            </div>
          </div>

          {errorMessage ? (
            <div className="no-print rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200">
              {errorMessage}
            </div>
          ) : null}

          <div className="no-print flex flex-wrap gap-2">
            <Button type="button" onClick={() => window.print()}>
              Imprimir
            </Button>
            {canCancel ? (
              <Button
                type="button"
                disabled={isCancelling}
                className="bg-red-600 text-white hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-600"
                onClick={() => void handleCancelSale()}
              >
                Cancelar venta
              </Button>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </>
  );
}
