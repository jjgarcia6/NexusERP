import { useEffect } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../features/auth";
import { CustomerList } from "../features/customers";

export function CustomersPage() {
  const { user } = useAuth();

  useEffect(() => {
    document.title = "NexusERP — Clientes";
  }, []);

  if (user?.role !== "admin" && user?.role !== "vendedor") {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
      <section className="mx-auto w-full max-w-6xl">
        <CustomerList />
      </section>
    </main>
  );
}
