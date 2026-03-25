import { isAxiosError } from "axios";
import { useMemo, useState } from "react";

import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { useAuth } from "../../auth";
import { useSuppliers } from "../hooks/useSuppliers";
import type { SupplierRequestType, SupplierType } from "../types/purchases.types";
import { SupplierForm } from "./SupplierForm";

export function SupplierList() {
  const { isAdmin } = useAuth();
  const { suppliers, isLoading, errorMessage: loadErrorMessage, createSupplier, updateSupplier } =
    useSuppliers();
  const [formOpen, setFormOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<SupplierType | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const sortedSuppliers = useMemo(
    () => [...suppliers].sort((a, b) => a.name.localeCompare(b.name, "es")),
    [suppliers]
  );

  async function handleSaveSupplier(payload: SupplierRequestType) {
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      if (editingSupplier) {
        await updateSupplier({
          supplierId: editingSupplier.id,
          payload,
        });
      } else {
        await createSupplier(payload);
      }
      setFormOpen(false);
      setEditingSupplier(null);
    } catch (error) {
      let message = "No fue posible guardar el proveedor.";
      
      if (isAxiosError(error)) {
        message = error.response?.data?.detail || error.message || message;
      } else if (error instanceof Error) {
        message = error.message;
      }
      
      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="space-y-4 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <header className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Proveedores</h2>
          <p className="text-sm text-slate-600 dark:text-slate-300">Gestiona proveedores para órdenes de compra.</p>
        </div>

        {isAdmin ? (
          <Button
            type="button"
            onClick={() => {
              setEditingSupplier(null);
              setFormOpen(true);
            }}
          >
            Nuevo proveedor
          </Button>
        ) : null}
      </header>

      {loadErrorMessage ? <p className="text-sm text-red-600 dark:text-red-400">{loadErrorMessage}</p> : null}
      {errorMessage ? <p className="text-sm text-red-600 dark:text-red-400">{errorMessage}</p> : null}

      {isLoading ? (
        <p className="text-sm text-slate-600 dark:text-slate-300">Cargando proveedores...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nombre</TableHead>
              <TableHead>RUC</TableHead>
              <TableHead>Contacto</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Estado</TableHead>
              {isAdmin ? <TableHead>Acciones</TableHead> : null}
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedSuppliers.map((supplier) => (
              <TableRow key={supplier.id}>
                <TableCell className="font-medium">{supplier.name}</TableCell>
                <TableCell>{supplier.ruc ?? "-"}</TableCell>
                <TableCell>{supplier.contact_name ?? "-"}</TableCell>
                <TableCell>{supplier.contact_email ?? "-"}</TableCell>
                <TableCell>
                  <Badge variant={supplier.is_active ? "success" : "muted"}>
                    {supplier.is_active ? "Activo" : "Inactivo"}
                  </Badge>
                </TableCell>

                {isAdmin ? (
                  <TableCell>
                    <Button
                      type="button"
                      className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                      onClick={() => {
                        setEditingSupplier(supplier);
                        setFormOpen(true);
                      }}
                    >
                      Editar
                    </Button>
                  </TableCell>
                ) : null}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <SupplierForm
        open={formOpen}
        onOpenChange={(next) => {
          setFormOpen(next);
          if (!next) {
            setEditingSupplier(null);
          }
        }}
        initialValues={editingSupplier}
        isPending={isSubmitting}
        onSubmitSupplier={handleSaveSupplier}
      />
    </section>
  );
}
