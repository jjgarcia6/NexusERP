import { isAxiosError } from "axios";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { useAuth } from "../../auth";
import { useCustomers } from "../hooks/useCustomers";
import type { CustomerRequestType, CustomerType } from "../types/customers.types";
import { CustomerForm } from "./CustomerForm";

const PAGE_SIZE = 20;

function customerTypeLabel(customerType: CustomerType["customer_type"]): string {
  return customerType === "persona_natural" ? "Persona Natural" : "Juridico";
}

function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!isAxiosError(error)) {
    return fallback;
  }

  const detail = error.response?.data?.detail;
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: string };
    if (typeof first?.msg === "string" && first.msg.trim()) {
      return first.msg;
    }
  }

  return fallback;
}

export function CustomerList() {
  const { user } = useAuth();
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [skip, setSkip] = useState(0);
  const [formOpen, setFormOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<CustomerType | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
      setSkip(0);
    }, 300);

    return () => window.clearTimeout(timeout);
  }, [searchInput]);

  const queryParams = useMemo(
    () => ({
      search: debouncedSearch || undefined,
      skip,
      limit: PAGE_SIZE,
    }),
    [debouncedSearch, skip],
  );

  const { customers, total, isLoading, createCustomer, updateCustomer } = useCustomers(queryParams);

  const canCreateOrEdit = user?.role === "admin" || user?.role === "vendedor";
  const canDeactivate = user?.role === "admin";

  async function handleCreate(payload: CustomerRequestType) {
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      await createCustomer(payload);
      setFormOpen(false);
      setEditingCustomer(null);
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, "No fue posible crear el cliente."));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdate(payload: {
    name?: string;
    email?: string;
    phone?: string;
    address?: string;
  }) {
    if (!editingCustomer) {
      return;
    }

    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      await updateCustomer({ customerId: editingCustomer.id, payload });
      setFormOpen(false);
      setEditingCustomer(null);
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, "No fue posible actualizar el cliente."));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeactivate(customer: CustomerType) {
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      await updateCustomer({
        customerId: customer.id,
        payload: { is_active: false },
      });
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, "No fue posible desactivar el cliente."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="space-y-4 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Clientes</h2>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Gestiona clientes para ventas, historial y facturacion.
          </p>
        </div>
        {canCreateOrEdit ? (
          <Button
            type="button"
            onClick={() => {
              setEditingCustomer(null);
              setFormOpen(true);
            }}
          >
            Nuevo cliente
          </Button>
        ) : null}
      </header>

      <Label className="flex flex-col gap-2">
        Buscar
        <Input
          value={searchInput}
          onChange={(event) => setSearchInput(event.target.value)}
          placeholder="Buscar por nombre o identificacion"
        />
      </Label>

      {errorMessage ? <p className="text-sm text-red-600 dark:text-red-400">{errorMessage}</p> : null}

      {isLoading ? (
        <p className="text-sm text-slate-600 dark:text-slate-300">Cargando clientes...</p>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Identificacion</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {customers.map((customer) => (
                <TableRow key={customer.id}>
                  <TableCell className="font-medium">{customer.name}</TableCell>
                  <TableCell>
                    <Badge
                      className={
                        customer.customer_type === "persona_natural"
                          ? "bg-teal-200 text-teal-900 dark:bg-teal-900/60 dark:text-teal-100"
                          : "bg-fuchsia-200 text-fuchsia-900 dark:bg-fuchsia-900/60 dark:text-fuchsia-100"
                      }
                    >
                      {customerTypeLabel(customer.customer_type)}
                    </Badge>
                  </TableCell>
                  <TableCell>{customer.identification_number}</TableCell>
                  <TableCell>{customer.email ?? "-"}</TableCell>
                  <TableCell>
                    <Badge
                      className={
                        customer.is_active
                          ? "bg-emerald-200 text-emerald-900 dark:bg-emerald-900/60 dark:text-emerald-100"
                          : "bg-slate-300 text-slate-700 dark:bg-slate-800 dark:text-slate-200"
                      }
                    >
                      {customer.is_active ? "Activo" : "Inactivo"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-2">
                      {canCreateOrEdit ? (
                        <Button
                          type="button"
                          className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                          onClick={() => {
                            setEditingCustomer(customer);
                            setFormOpen(true);
                          }}
                        >
                          Editar
                        </Button>
                      ) : null}

                      {canDeactivate && customer.is_active ? (
                        <Button
                          type="button"
                          className="bg-red-600 text-white hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-600"
                          disabled={isSubmitting}
                          onClick={() => {
                            void handleDeactivate(customer);
                          }}
                        >
                          Desactivar
                        </Button>
                      ) : null}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="flex items-center justify-between pt-2">
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Mostrando {customers.length} de {total} clientes
            </p>
            <div className="flex gap-2">
              <Button
                type="button"
                className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                onClick={() => setSkip((previous) => Math.max(previous - PAGE_SIZE, 0))}
                disabled={skip === 0}
              >
                Anterior
              </Button>
              <Button
                type="button"
                onClick={() => setSkip((previous) => previous + PAGE_SIZE)}
                disabled={skip + PAGE_SIZE >= total}
              >
                Siguiente
              </Button>
            </div>
          </div>
        </>
      )}

      <CustomerForm
        open={formOpen}
        onOpenChange={(nextOpen) => {
          setFormOpen(nextOpen);
          if (!nextOpen) {
            setEditingCustomer(null);
            setErrorMessage(null);
          }
        }}
        initialValues={editingCustomer}
        isPending={isSubmitting}
        submitError={errorMessage}
        onSubmitCreate={handleCreate}
        onSubmitUpdate={handleUpdate}
      />
    </section>
  );
}
