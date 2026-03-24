import { useEffect } from "react";

import { RegisterForm } from "../features/auth";

export function RegisterPage() {
  useEffect(() => {
    document.title = "NexusERP - Registro";
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-12 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <section className="mx-auto flex w-full max-w-4xl flex-col items-center gap-6">
        <h1 className="text-3xl font-semibold tracking-tight">Crear cuenta en NexusERP</h1>
        <RegisterForm />
      </section>
    </main>
  );
}
