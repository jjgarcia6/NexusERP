import { HealthStatusCard } from "../features/bootstrap/components/HealthStatusCard";

export function PlaceholderPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-12 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <section className="mx-auto flex w-full max-w-3xl flex-col gap-6">
        <h1 className="text-4xl font-semibold tracking-tight">NexusERP</h1>
        <HealthStatusCard />
      </section>
    </main>
  );
}
