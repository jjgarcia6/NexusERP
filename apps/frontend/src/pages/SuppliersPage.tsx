import { useEffect } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../features/auth";
import { SupplierList } from "../features/purchases/components/SupplierList";

export function SuppliersPage() {
  const { user } = useAuth();

  useEffect(() => {
    document.title = "NexusERP — Proveedores";
  }, []);

  if (user?.role !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
      <section className="mx-auto w-full max-w-6xl">
        <SupplierList />
      </section>
    </main>
  );
}
