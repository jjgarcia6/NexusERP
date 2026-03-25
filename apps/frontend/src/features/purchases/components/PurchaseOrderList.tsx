import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button } from "../../../components/ui/button";
import { Label } from "../../../components/ui/label";
import { Select } from "../../../components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { useAuth } from "../../auth";
import { usePurchaseOrders } from "../hooks/usePurchaseOrders";
import { useSuppliers } from "../hooks/useSuppliers";
import { orderStatusSchema, type OrderStatusType, type PurchaseOrderRequestType } from "../types/purchases.types";
import { OrderStatusBadge } from "./OrderStatusBadge";
import { PurchaseOrderForm } from "./PurchaseOrderForm";

const PAGE_SIZE = 20;

function formatMoney(value: number): string {
  return `$${value.toFixed(2)}`;
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString("es-EC");
}

export function PurchaseOrderList() {
  const navigate = useNavigate();
  const { user, isAdmin } = useAuth();
  const { suppliers, isLoading: suppliersLoading } = useSuppliers();
  const [statusFilter, setStatusFilter] = useState<OrderStatusType | "">("");
  const [supplierFilter, setSupplierFilter] = useState("");
  const [skip, setSkip] = useState(0);
  const [formOpen, setFormOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const queryParams = useMemo(
    () => ({
      status: statusFilter || undefined,
      supplier_id: supplierFilter || undefined,
      skip,
      limit: PAGE_SIZE,
    }),
    [statusFilter, supplierFilter, skip]
  );

  const { orders, total, isLoading, errorMessage: loadErrorMessage, createOrder, confirmOrder, receiveOrder, cancelOrder } =
    usePurchaseOrders(queryParams);

  const activeSuppliers = useMemo(() => suppliers.filter((supplier) => supplier.is_active), [suppliers]);

  async function handleCreateOrder(payload: PurchaseOrderRequestType) {
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      await createOrder(payload);
      setFormOpen(false);
    } catch {
      setErrorMessage("No fue posible crear la orden de compra.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleConfirmOrder(orderId: string) {
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      await confirmOrder(orderId);
    } catch {
      setErrorMessage("No fue posible confirmar la orden.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleReceiveOrder(orderId: string) {
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const result = await receiveOrder(orderId);
      if (!result.ok) {
        setErrorMessage(result.message ?? "No se pudo actualizar el inventario. Intente nuevamente");
      }
    } catch {
      setErrorMessage("No fue posible recibir la orden.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCancelOrder(orderId: string) {
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      await cancelOrder(orderId);
    } catch {
      setErrorMessage("No fue posible cancelar la orden.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="space-y-4 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Órdenes de compra</h2>
          <p className="text-sm text-slate-600 dark:text-slate-300">Filtra, revisa y gestiona el flujo de compras.</p>
        </div>

        {isAdmin ? (
          <Button
            type="button"
            onClick={() => {
              setFormOpen(true);
            }}
          >
            Nueva orden
          </Button>
        ) : null}
      </header>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <Label className="flex flex-col gap-2">
          Estado
          <Select
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value as OrderStatusType | "");
              setSkip(0);
            }}
          >
            <option value="">Todos</option>
            {orderStatusSchema.options.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </Select>
        </Label>

        <Label className="flex flex-col gap-2">
          Proveedor
          <Select
            value={supplierFilter}
            disabled={suppliersLoading}
            onChange={(event) => {
              setSupplierFilter(event.target.value);
              setSkip(0);
            }}
          >
            <option value="">Todos</option>
            {activeSuppliers.map((supplier) => (
              <option key={supplier.id} value={supplier.id}>
                {supplier.name}
              </option>
            ))}
          </Select>
        </Label>
      </div>

      {loadErrorMessage ? (
        <div className="rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200">
          {loadErrorMessage}
        </div>
      ) : null}

      {errorMessage ? (
        <div className="rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200">
          {errorMessage}
        </div>
      ) : null}

      {isLoading ? (
        <p className="text-sm text-slate-600 dark:text-slate-300">Cargando órdenes...</p>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Proveedor</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Fecha</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {orders.map((order) => {
                const canConfirm = isAdmin && order.status === "draft";
                const canReceive = (user?.role === "admin" || user?.role === "bodeguero") && order.status === "confirmed";
                const canCancel = isAdmin && (order.status === "draft" || order.status === "confirmed");

                return (
                  <TableRow key={order.id} className="cursor-pointer" onClick={() => navigate(`/purchases/${order.id}`)}>
                    <TableCell className="font-medium">{order.id.slice(-8).toUpperCase()}</TableCell>
                    <TableCell>{order.supplier_name}</TableCell>
                    <TableCell>
                      <OrderStatusBadge status={order.status} />
                    </TableCell>
                    <TableCell>{formatMoney(order.total)}</TableCell>
                    <TableCell>{formatDate(order.created_at)}</TableCell>
                    <TableCell onClick={(event) => event.stopPropagation()}>
                      <div className="flex flex-wrap gap-2">
                        {canConfirm ? (
                          <Button type="button" disabled={isSubmitting} onClick={() => void handleConfirmOrder(order.id)}>
                            Confirmar
                          </Button>
                        ) : null}

                        {canReceive ? (
                          <Button type="button" disabled={isSubmitting} onClick={() => void handleReceiveOrder(order.id)}>
                            Recibir
                          </Button>
                        ) : null}

                        {canCancel ? (
                          <Button
                            type="button"
                            disabled={isSubmitting}
                            className="bg-red-600 text-white hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-600"
                            onClick={() => void handleCancelOrder(order.id)}
                          >
                            Cancelar
                          </Button>
                        ) : null}
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>

          <div className="flex items-center justify-between pt-2">
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Mostrando {orders.length} de {total} órdenes
            </p>
            <div className="flex gap-2">
              <Button
                type="button"
                className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                onClick={() => setSkip((prev) => Math.max(prev - PAGE_SIZE, 0))}
                disabled={skip === 0}
              >
                Anterior
              </Button>
              <Button
                type="button"
                onClick={() => setSkip((prev) => prev + PAGE_SIZE)}
                disabled={skip + PAGE_SIZE >= total}
              >
                Siguiente
              </Button>
            </div>
          </div>
        </>
      )}

      <PurchaseOrderForm
        open={formOpen}
        onOpenChange={setFormOpen}
        isPending={isSubmitting}
        onSubmitOrder={handleCreateOrder}
      />
    </section>
  );
}
