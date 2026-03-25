import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import type { RoleType } from "../../auth";
import type { PurchaseOrderType } from "../types/purchases.types";
import { OrderStatusBadge } from "./OrderStatusBadge";

type PurchaseOrderDetailProps = {
  order: PurchaseOrderType;
  role?: RoleType;
  isActionPending?: boolean;
  actionErrorMessage?: string | null;
  onConfirm?: (orderId: string) => Promise<void>;
  onReceive?: (orderId: string) => Promise<void>;
  onCancel?: (orderId: string) => Promise<void>;
};

function formatDate(dateValue: string | null): string {
  if (!dateValue) {
    return "-";
  }
  return new Date(dateValue).toLocaleString("es-EC");
}

function formatMoney(value: number): string {
  return `$${value.toFixed(2)}`;
}

export function PurchaseOrderDetail({
  order,
  role,
  isActionPending = false,
  actionErrorMessage,
  onConfirm,
  onReceive,
  onCancel,
}: PurchaseOrderDetailProps) {
  const canConfirm = role === "admin" && order.status === "draft" && Boolean(onConfirm);
  const canReceive = (role === "admin" || role === "bodeguero") && order.status === "confirmed" && Boolean(onReceive);
  const canCancel = role === "admin" && (order.status === "draft" || order.status === "confirmed") && Boolean(onCancel);

  return (
    <Card>
      <CardHeader className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="space-y-1">
          <CardTitle>Orden #{order.id.slice(-8).toUpperCase()}</CardTitle>
          <p className="text-sm text-slate-600 dark:text-slate-300">Proveedor: {order.supplier_name}</p>
        </div>
        <OrderStatusBadge status={order.status} />
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
          <p>
            <span className="font-semibold">Creada:</span> {formatDate(order.created_at)}
          </p>
          <p>
            <span className="font-semibold">Confirmada:</span> {formatDate(order.confirmed_at)}
          </p>
          <p>
            <span className="font-semibold">Recibida:</span> {formatDate(order.received_at)}
          </p>
          <p>
            <span className="font-semibold">Cancelada:</span> {formatDate(order.cancelled_at)}
          </p>
          <p className="md:col-span-2">
            <span className="font-semibold">Notas:</span> {order.notes ?? "Sin notas"}
          </p>
          <p className="md:col-span-2 text-lg font-semibold text-slate-900 dark:text-slate-100">
            Total: {formatMoney(order.total)}
          </p>
        </div>

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
            {order.lines.map((line) => (
              <TableRow key={`${line.product_id}-${line.product_name}`}>
                <TableCell className="font-medium">{line.product_name}</TableCell>
                <TableCell>{line.quantity}</TableCell>
                <TableCell>{formatMoney(line.unit_cost)}</TableCell>
                <TableCell>{formatMoney(line.subtotal)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {actionErrorMessage ? (
          <div className="rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200">
            {actionErrorMessage}
          </div>
        ) : null}

        {canConfirm || canReceive || canCancel ? (
          <div className="flex flex-wrap gap-2">
            {canConfirm ? (
              <Button type="button" disabled={isActionPending} onClick={() => void onConfirm?.(order.id)}>
                Confirmar
              </Button>
            ) : null}

            {canReceive ? (
              <Button type="button" disabled={isActionPending} onClick={() => void onReceive?.(order.id)}>
                Recibir
              </Button>
            ) : null}

            {canCancel ? (
              <Button
                type="button"
                disabled={isActionPending}
                className="bg-red-600 text-white hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-600"
                onClick={() => void onCancel?.(order.id)}
              >
                Cancelar
              </Button>
            ) : null}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
