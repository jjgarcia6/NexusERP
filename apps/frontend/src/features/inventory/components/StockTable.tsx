import { useQueryClient } from "@tanstack/react-query";
import { isAxiosError } from "axios";
import { useMemo, useState } from "react";

import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { useAuth } from "../../auth";
import { useProducts } from "../../catalog/hooks/useProducts";
import { useStockLevels } from "../hooks/useStockLevels";
import { useStockMovements } from "../hooks/useStockMovements";
import type { StockMovementRequestType } from "../types/inventory.types";
import { StockInitForm } from "./StockInitForm";
import { StockMovementForm } from "./StockMovementForm";

export function StockTable() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { products, isLoading: productsLoading } = useProducts({ skip: 0, limit: 100 });
  const { stockLevels, isLoading, initializeStock } = useStockLevels({ skip: 0, limit: 100 });
  const { registerMovement } = useStockMovements({ skip: 0, limit: 20 });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [movementOpen, setMovementOpen] = useState(false);
  const [initOpen, setInitOpen] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState<string | undefined>(undefined);

  const stockByProductId = useMemo(
    () => new Map(stockLevels.map((item) => [item.product_id, item])),
    [stockLevels],
  );

  const rows = useMemo(
    () => products.map((product) => {
      const level = stockByProductId.get(product.id);
      return {
        productId: product.id,
        productName: product.name,
        available_quantity: level?.available_quantity,
        min_stock: level?.min_stock ?? product.min_stock ?? 0,
        low_stock: level?.low_stock ?? false,
      };
    }),
    [products, stockByProductId],
  );

  const movementProducts = useMemo(
    () => stockLevels.filter((item) => typeof item.available_quantity === "number"),
    [stockLevels],
  );

  const selectedProductName = useMemo(() => {
    if (!selectedProductId) {
      return "producto";
    }
    return rows.find((row) => row.productId === selectedProductId)?.productName ?? "producto";
  }, [rows, selectedProductId]);

  async function handleInitializeStock(payload: { quantity: number; min_stock: number }) {
    if (!selectedProductId) {
      return;
    }

    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      await initializeStock({ productId: selectedProductId, payload });
      setInitOpen(false);
      setSelectedProductId(undefined);
    } catch (error) {
      let message = "No fue posible inicializar el stock.";

      if (isAxiosError(error)) {
        const detail = error.response?.data?.detail;
        if (typeof detail === "string") {
          message = detail;
        }

        if (error.response?.status === 409) {
          await queryClient.invalidateQueries({ queryKey: ["stock"] });
          setInitOpen(false);
          setSelectedProductId(undefined);
        }
      }

      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRegisterMovement(payload: StockMovementRequestType) {
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      await registerMovement(payload);
      setMovementOpen(false);
      setSelectedProductId(undefined);
    } catch {
      setErrorMessage("No fue posible registrar el movimiento.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="space-y-4 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <header>
        <h2 className="text-2xl font-semibold tracking-tight">Stock actual</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">Consulta niveles de stock y acciones rápidas.</p>
      </header>

      {errorMessage ? (
        <div className="rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200">
          {errorMessage}
        </div>
      ) : null}

      {isLoading || productsLoading ? (
        <p className="text-sm text-slate-600 dark:text-slate-300">Cargando stock...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Producto</TableHead>
              <TableHead>Disponible</TableHead>
              <TableHead>Mínimo</TableHead>
              <TableHead>Alerta</TableHead>
              <TableHead>Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => {
              const canInitialize = user?.role === "admin" && typeof row.available_quantity !== "number";
              const canMove = (user?.role === "admin" || user?.role === "bodeguero") && typeof row.available_quantity === "number";

              return (
                <TableRow key={row.productId}>
                  <TableCell className="font-medium">{row.productName}</TableCell>
                  <TableCell>{typeof row.available_quantity === "number" ? row.available_quantity : "No inicializado"}</TableCell>
                  <TableCell>{row.min_stock}</TableCell>
                  <TableCell>
                    <Badge
                      variant={row.low_stock ? "default" : "success"}
                      className={
                        row.low_stock
                          ? "bg-red-200 text-red-900 dark:bg-red-900/60 dark:text-red-100"
                          : undefined
                      }
                    >
                      {row.low_stock ? "Stock bajo" : "OK"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-2">
                      {canMove ? (
                        <Button
                          type="button"
                          onClick={() => {
                            setSelectedProductId(row.productId);
                            setMovementOpen(true);
                          }}
                        >
                          Registrar movimiento
                        </Button>
                      ) : null}

                      {canInitialize ? (
                        <Button
                          type="button"
                          className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                          onClick={() => {
                            setSelectedProductId(row.productId);
                            setInitOpen(true);
                          }}
                        >
                          Inicializar
                        </Button>
                      ) : null}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      <StockInitForm
        open={initOpen}
        onOpenChange={setInitOpen}
        productName={selectedProductName}
        isPending={isSubmitting}
        onSubmitInit={handleInitializeStock}
      />

      <StockMovementForm
        open={movementOpen}
        onOpenChange={setMovementOpen}
        products={movementProducts}
        defaultProductId={selectedProductId}
        isPending={isSubmitting}
        onSubmitMovement={handleRegisterMovement}
      />
    </section>
  );
}
