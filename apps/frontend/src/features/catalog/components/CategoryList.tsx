import { useMemo, useState } from "react";

import { Button } from "../../../components/ui/button";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../../../components/ui/alert-dialog";
import { Badge } from "../../../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { useAuth } from "../../auth";
import { useCategories } from "../hooks/useCategories";
import type { CategoryType } from "../types/catalog.types";
import { CategoryForm } from "./CategoryForm";

export function CategoryList() {
  const { isAdmin } = useAuth();
  const { categories, isLoading, createCategory, updateCategory, deleteCategory } = useCategories();
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<CategoryType | null>(null);
  const [categoryToDelete, setCategoryToDelete] = useState<CategoryType | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const sortedCategories = useMemo(
    () => [...categories].sort((a, b) => a.name.localeCompare(b.name, "es")),
    [categories]
  );

  async function handleSave(payload: { name: string; description?: string }) {
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      if (editing) {
        await updateCategory({ categoryId: editing.id, payload });
      } else {
        await createCategory(payload);
      }
      setFormOpen(false);
      setEditing(null);
    } catch {
      setErrorMessage("No fue posible guardar la categoría.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete() {
    if (!categoryToDelete) {
      return;
    }
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      await deleteCategory(categoryToDelete.id);
      setCategoryToDelete(null);
    } catch {
      setErrorMessage("No fue posible eliminar la categoría.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="space-y-4 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <header className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Categorías</h2>
          <p className="text-sm text-slate-600 dark:text-slate-300">Administra categorías para organizar productos.</p>
        </div>
        {isAdmin ? (
          <Button
            type="button"
            onClick={() => {
              setEditing(null);
              setFormOpen(true);
            }}
          >
            Nueva categoría
          </Button>
        ) : null}
      </header>

      {errorMessage ? <p className="text-sm text-red-600 dark:text-red-400">{errorMessage}</p> : null}

      {isLoading ? (
        <p className="text-sm text-slate-600 dark:text-slate-300">Cargando categorías...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nombre</TableHead>
              <TableHead>Descripción</TableHead>
              <TableHead>Estado</TableHead>
              {isAdmin ? <TableHead>Acciones</TableHead> : null}
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedCategories.map((category) => (
              <TableRow key={category.id}>
                <TableCell className="font-medium">{category.name}</TableCell>
                <TableCell>{category.description ?? "Sin descripción"}</TableCell>
                <TableCell>
                  <Badge variant={category.is_active ? "success" : "muted"}>
                    {category.is_active ? "Activa" : "Inactiva"}
                  </Badge>
                </TableCell>
                {isAdmin ? (
                  <TableCell className="flex gap-2">
                    <Button
                      type="button"
                      className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                      onClick={() => {
                        setEditing(category);
                        setFormOpen(true);
                      }}
                    >
                      Editar
                    </Button>
                    <Button
                      type="button"
                      className="bg-red-600 text-white hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-600"
                      onClick={() => {
                        setCategoryToDelete(category);
                      }}
                    >
                      Eliminar
                    </Button>
                  </TableCell>
                ) : null}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <CategoryForm
        open={formOpen}
        onOpenChange={(next) => {
          setFormOpen(next);
          if (!next) {
            setEditing(null);
          }
        }}
        initialValues={editing}
        isPending={isSubmitting}
        onSubmitCategory={handleSave}
      />

      <AlertDialog open={Boolean(categoryToDelete)} onOpenChange={(next) => !next && setCategoryToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Eliminar categoría</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción no se puede deshacer. Se eliminará la categoría seleccionada.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <Button
              type="button"
              className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
              onClick={() => setCategoryToDelete(null)}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              disabled={isSubmitting}
              className="bg-red-600 text-white hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-600"
              onClick={() => {
                void handleDelete();
              }}
            >
              Confirmar eliminación
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </section>
  );
}
