import { useEffect } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import { Button } from "../components/ui/button";
import { useAuth } from "../features/auth";
import { SaleDetail, SaleList, useSales } from "../features/sales";

export function SalesPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const { sale, isLoading } = useSales({ saleId: id });

  useEffect(() => {
    document.title = "NexusERP — Ventas";
  }, []);

  if (user?.role !== "admin" && user?.role !== "vendedor" && user?.role !== "bodeguero") {
    return <Navigate to="/dashboard" replace />;
  }

  if (!id) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
        <section className="mx-auto w-full max-w-6xl">
          <SaleList />
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
      <section className="mx-auto w-full max-w-6xl space-y-4">
        <Button
          type="button"
          className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
          onClick={() => navigate("/sales")}
        >
          Volver al listado
        </Button>

        {isLoading ? (
          <p className="text-sm text-slate-600 dark:text-slate-300">Cargando venta...</p>
        ) : sale ? (
          <SaleDetail
            sale={sale}
            role={user?.role}
            onCancelled={() => {
              navigate(`/sales/${id}`, { replace: true });
            }}
          />
        ) : (
          <p className="text-sm text-red-600 dark:text-red-400">No se pudo cargar el detalle de la venta.</p>
        )}
      </section>
    </main>
  );
}
