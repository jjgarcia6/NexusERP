import { useEffect } from "react";

import { CategoryList } from "../features/catalog";

export function CategoriesPage() {
  useEffect(() => {
    document.title = "NexusERP — Categorías";
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 md:px-6">
      <section className="mx-auto w-full max-w-6xl">
        <CategoryList />
      </section>
    </main>
  );
}
