import { useHealthCheck } from "../hooks/useHealthCheck";

export function HealthStatusCard() {
  const { status, isLoading } = useHealthCheck();

  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-300 bg-white p-6 text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">
        Cargando estado del sistema...
      </div>
    );
  }

  if (status === "ok") {
    return (
      <div className="rounded-xl border border-emerald-300 bg-emerald-50 p-6 text-emerald-900 dark:border-emerald-700 dark:bg-emerald-950 dark:text-emerald-100">
        Sistema operativo
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-amber-300 bg-amber-50 p-6 text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-100">
      Sin conexión
    </div>
  );
}
