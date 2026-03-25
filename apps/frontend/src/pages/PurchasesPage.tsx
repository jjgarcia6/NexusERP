import { useEffect, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import { Button } from "../components/ui/button";
import { useAuth } from "../features/auth";
import { PurchaseOrderDetail } from "../features/purchases/components/PurchaseOrderDetail";
import { PurchaseOrderList } from "../features/purchases/components/PurchaseOrderList";
import { usePurchaseOrders } from "../features/purchases/hooks/usePurchaseOrders";

export function PurchasesPage() {
  const navigate = useNavigate();
  const { orderId } = useParams<{ orderId: string }>();
  const { user } = useAuth();
  const [isActionPending, setIsActionPending] = useState(false);
  const [actionErrorMessage, setActionErrorMessage] = useState<string | null>(null);

  const {
    order,
    isOrderLoading,
    confirmOrder,
    receiveOrder,
    cancelOrder,
  } = usePurchaseOrders({
    orderId,
    skip: 0,
    limit: 20,
  });

  useEffect(() => {
    document.title = "NexusERP — Compras";
  }, []);

  if (user?.role !== "admin" && user?.role !== "bodeguero") {
    return <Navigate to="/dashboard" replace />;
  }

  if (!orderId) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
        <section className="mx-auto w-full max-w-6xl">
          <PurchaseOrderList />
        </section>
      </main>
    );
  }

  async function handleConfirm(selectedOrderId: string) {
    setActionErrorMessage(null);
    setIsActionPending(true);

    try {
      await confirmOrder(selectedOrderId);
    } catch {
      setActionErrorMessage("No fue posible confirmar la orden.");
    } finally {
      setIsActionPending(false);
    }
  }

  async function handleReceive(selectedOrderId: string) {
    setActionErrorMessage(null);
    setIsActionPending(true);

    try {
      const result = await receiveOrder(selectedOrderId);
      if (!result.ok) {
        setActionErrorMessage(result.message ?? "No se pudo actualizar el inventario. Intente nuevamente");
      }
    } catch {
      setActionErrorMessage("No fue posible recibir la orden.");
    } finally {
      setIsActionPending(false);
    }
  }

  async function handleCancel(selectedOrderId: string) {
    setActionErrorMessage(null);
    setIsActionPending(true);

    try {
      await cancelOrder(selectedOrderId);
    } catch {
      setActionErrorMessage("No fue posible cancelar la orden.");
    } finally {
      setIsActionPending(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
      <section className="mx-auto w-full max-w-6xl space-y-4">
        <Button
          type="button"
          className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
          onClick={() => navigate("/purchases")}
        >
          Volver al listado
        </Button>

        {isOrderLoading ? (
          <p className="text-sm text-slate-600 dark:text-slate-300">Cargando orden...</p>
        ) : order ? (
          <PurchaseOrderDetail
            order={order}
            role={user?.role}
            isActionPending={isActionPending}
            actionErrorMessage={actionErrorMessage}
            onConfirm={handleConfirm}
            onReceive={handleReceive}
            onCancel={handleCancel}
          />
        ) : (
          <p className="text-sm text-red-600 dark:text-red-400">No se pudo cargar el detalle de la orden.</p>
        )}
      </section>
    </main>
  );
}
