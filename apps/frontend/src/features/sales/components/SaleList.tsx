import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Select } from "../../../components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { CustomerSelector } from "../../customers";
import type { CustomerSearchResultType } from "../../customers";
import { useSales } from "../hooks/useSales";
import type { SaleStatusType } from "../types/sales.types";

const PAGE_SIZE = 20;

function formatMoney(value: number): string {
  return `$${value.toFixed(2)}`;
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString("es-EC");
}

function statusLabel(status: SaleStatusType): string {
  if (status === "draft") {
    return "Borrador";
  }
  if (status === "confirmed") {
    return "Confirmada";
  }
  return "Cancelada";
}

function statusClassName(status: SaleStatusType): string {
  if (status === "confirmed") {
    return "bg-green-200 text-green-900 dark:bg-green-800 dark:text-green-100";
  }
  if (status === "cancelled") {
    return "bg-red-200 text-red-900 dark:bg-red-800 dark:text-red-100";
  }
  return "bg-slate-300 text-slate-900 dark:bg-slate-700 dark:text-slate-100";
}

export function SaleList() {
  const navigate = useNavigate();
  const [status, setStatus] = useState<SaleStatusType | "">("");
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerSearchResultType | null>(null);
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [skip, setSkip] = useState(0);

  const queryParams = useMemo(
    () => ({
      status: status || undefined,
      customer_id: selectedCustomer?.id,
      from: fromDate || undefined,
      to: toDate || undefined,
      skip,
      limit: PAGE_SIZE,
    }),
    [fromDate, selectedCustomer?.id, skip, status, toDate]
  );

  const { sales, total, isLoading } = useSales(queryParams);

  return (
    <section className="space-y-4 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <header className="space-y-1">
        <h2 className="text-2xl font-semibold tracking-tight">Ventas</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Filtra ventas por estado, cliente y rango de fechas.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
        <label className="flex flex-col gap-2 text-sm">
          Estado
          <Select
            value={status}
            onChange={(event) => {
              setStatus(event.target.value as SaleStatusType | "");
              setSkip(0);
            }}
          >
            <option value="">Todos</option>
            <option value="draft">Borrador</option>
            <option value="confirmed">Confirmada</option>
            <option value="cancelled">Cancelada</option>
          </Select>
        </label>

        <label className="flex flex-col gap-2 text-sm lg:col-span-2">
          Cliente
          <CustomerSelector
            onSelect={(customer) => {
              setSelectedCustomer(customer);
              setSkip(0);
            }}
            placeholder="Buscar cliente para filtrar"
          />
        </label>

        <div className="grid grid-cols-2 gap-2">
          <label className="flex flex-col gap-2 text-sm">
            Desde
            <Input
              type="date"
              value={fromDate}
              onChange={(event) => {
                setFromDate(event.target.value);
                setSkip(0);
              }}
            />
          </label>
          <label className="flex flex-col gap-2 text-sm">
            Hasta
            <Input
              type="date"
              value={toDate}
              onChange={(event) => {
                setToDate(event.target.value);
                setSkip(0);
              }}
            />
          </label>
        </div>
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-600 dark:text-slate-300">Cargando ventas...</p>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Comprobante</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Fecha</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sales.map((sale) => (
                <TableRow key={sale.id} className="cursor-pointer" onClick={() => navigate(`/sales/${sale.id}`)}>
                  <TableCell className="font-medium">{sale.invoice_number ?? "PENDIENTE"}</TableCell>
                  <TableCell>{sale.customer_name}</TableCell>
                  <TableCell>{formatMoney(sale.total)}</TableCell>
                  <TableCell>
                    <Badge className={statusClassName(sale.status)}>{statusLabel(sale.status)}</Badge>
                  </TableCell>
                  <TableCell>{formatDate(sale.created_at)}</TableCell>
                  <TableCell onClick={(event) => event.stopPropagation()}>
                    <Button
                      type="button"
                      className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                      onClick={() => navigate(`/sales/${sale.id}`)}
                    >
                      Ver detalle
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="flex items-center justify-between gap-3 pt-2">
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Mostrando {sales.length} de {total} ventas
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
    </section>
  );
}
