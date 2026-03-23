import { useEffect } from "react";

import { LoginForm } from "../features/auth";

export function LoginPage() {
  useEffect(() => {
    document.title = "NexusERP - Iniciar sesión";
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-12 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <section className="mx-auto flex w-full max-w-4xl flex-col items-center gap-6">
        <h1 className="text-3xl font-semibold tracking-tight">Acceso a NexusERP</h1>
        <LoginForm />
      </section>
    </main>
  );
}
