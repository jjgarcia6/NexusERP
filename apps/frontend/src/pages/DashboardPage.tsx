import { useEffect } from "react";

import { useAuth } from "../features/auth";

export function DashboardPage() {
  const { user, logout, isLoading } = useAuth();

  useEffect(() => {
    document.title = "NexusERP - Dashboard";
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-12 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <section className="mx-auto flex w-full max-w-3xl flex-col gap-6 rounded-2xl border border-slate-300 bg-white p-8 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h1 className="text-3xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-base text-slate-700 dark:text-slate-300">
          Usuario: <span className="font-semibold">{user?.full_name ?? "Desconocido"}</span>
        </p>
        <p className="text-base text-slate-700 dark:text-slate-300">
          Rol: <span className="font-semibold">{user?.role ?? "sin rol"}</span>
        </p>
        <button
          type="button"
          onClick={() => {
            void logout();
          }}
          disabled={isLoading}
          className="w-fit rounded-md bg-slate-900 px-4 py-2 font-medium text-white transition hover:bg-slate-800 disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200"
        >
          Cerrar sesión
        </button>
      </section>
    </main>
  );
}
