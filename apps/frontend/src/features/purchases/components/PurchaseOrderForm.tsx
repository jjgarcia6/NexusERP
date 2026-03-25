import { zodResolver } from "@hookform/resolvers/zod";
import { useMemo } from "react";
import { useFieldArray, useForm } from "react-hook-form";

import { Button } from "../../../components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../../../components/ui/dialog";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select } from "../../../components/ui/select";
import { Textarea } from "../../../components/ui/textarea";
import { useProducts } from "../../catalog/hooks/useProducts";
import { useSuppliers } from "../hooks/useSuppliers";
import {
  purchaseOrderRequestSchema,
  type PurchaseOrderRequestType,
} from "../types/purchases.types";

type PurchaseOrderFormProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isPending: boolean;
  onSubmitOrder: (payload: PurchaseOrderRequestType) => Promise<void>;
};

const DEFAULT_LINE = {
  product_id: "",
  quantity: 1,
  unit_cost: 0,
};

export function PurchaseOrderForm({
  open,
  onOpenChange,
  isPending,
  onSubmitOrder,
}: PurchaseOrderFormProps) {
  const { suppliers, isLoading: suppliersLoading } = useSuppliers();
  const { products, isLoading: productsLoading } = useProducts({
    skip: 0,
    limit: 100,
  });

  const activeSuppliers = useMemo(() => suppliers.filter((supplier) => supplier.is_active), [suppliers]);
  const activeProducts = useMemo(() => products.filter((product) => product.is_active), [products]);

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<PurchaseOrderRequestType>({
    resolver: zodResolver(purchaseOrderRequestSchema),
    defaultValues: {
      supplier_id: "",
      lines: [DEFAULT_LINE],
      notes: "",
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "lines",
  });

  const watchedLines = watch("lines");
  const visualTotal = useMemo(
    () =>
      (watchedLines ?? []).reduce((acc, line) => {
        const quantity = Number.isFinite(line.quantity) ? line.quantity : 0;
        const unitCost = Number.isFinite(line.unit_cost) ? line.unit_cost : 0;
        return acc + quantity * unitCost;
      }, 0),
    [watchedLines]
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Nueva orden de compra</DialogTitle>
          <DialogDescription>
            Define proveedor, líneas de producto y notas internas para registrar la orden.
          </DialogDescription>
        </DialogHeader>

        <form
          className="space-y-4"
          onSubmit={handleSubmit(async (data) => {
            await onSubmitOrder(data);
            reset({
              supplier_id: "",
              lines: [DEFAULT_LINE],
              notes: "",
            });
          })}
        >
          <Label className="flex flex-col gap-2">
            Proveedor
            <Select {...register("supplier_id")} disabled={suppliersLoading}>
              <option value="">Seleccione un proveedor</option>
              {activeSuppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name}
                </option>
              ))}
            </Select>
            {errors.supplier_id ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.supplier_id.message}</span>
            ) : null}
          </Label>

          <div className="space-y-3 rounded-xl border border-slate-200 p-4 dark:border-slate-700">
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-base font-semibold">Líneas de productos</h3>
              <Button
                type="button"
                className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
                onClick={() => append(DEFAULT_LINE)}
              >
                Añadir línea
              </Button>
            </div>

            {fields.map((field, index) => (
              <div
                key={field.id}
                className="grid grid-cols-1 gap-3 rounded-lg border border-slate-200 p-3 dark:border-slate-700 md:grid-cols-12"
              >
                <Label className="flex flex-col gap-2 md:col-span-5">
                  Producto
                  <Select {...register(`lines.${index}.product_id`)} disabled={productsLoading}>
                    <option value="">Seleccione un producto</option>
                    {activeProducts.map((product) => (
                      <option key={product.id} value={product.id}>
                        {product.name}
                      </option>
                    ))}
                  </Select>
                  {errors.lines?.[index]?.product_id ? (
                    <span className="text-sm text-red-600 dark:text-red-400">
                      {errors.lines[index]?.product_id?.message}
                    </span>
                  ) : null}
                </Label>

                <Label className="flex flex-col gap-2 md:col-span-2">
                  Cantidad
                  <Input
                    type="number"
                    min="1"
                    step="1"
                    {...register(`lines.${index}.quantity`, {
                      setValueAs: (value) => Number(value),
                    })}
                  />
                  {errors.lines?.[index]?.quantity ? (
                    <span className="text-sm text-red-600 dark:text-red-400">
                      {errors.lines[index]?.quantity?.message}
                    </span>
                  ) : null}
                </Label>

                <Label className="flex flex-col gap-2 md:col-span-3">
                  Precio unitario
                  <Input
                    type="number"
                    min="0"
                    step="0.01"
                    {...register(`lines.${index}.unit_cost`, {
                      setValueAs: (value) => Number(value),
                    })}
                  />
                  {errors.lines?.[index]?.unit_cost ? (
                    <span className="text-sm text-red-600 dark:text-red-400">
                      {errors.lines[index]?.unit_cost?.message}
                    </span>
                  ) : null}
                </Label>

                <div className="flex items-end md:col-span-2 md:justify-end">
                  <Button
                    type="button"
                    className="w-full bg-red-600 text-white hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-600 md:w-auto"
                    onClick={() => remove(index)}
                    disabled={fields.length === 1}
                  >
                    Eliminar
                  </Button>
                </div>
              </div>
            ))}

            {errors.lines?.message ? (
              <p className="text-sm text-red-600 dark:text-red-400">{errors.lines.message}</p>
            ) : null}
          </div>

          <Label className="flex flex-col gap-2">
            Notas
            <Textarea placeholder="Observaciones internas (opcional)" {...register("notes")} />
            {errors.notes ? <span className="text-sm text-red-600 dark:text-red-400">{errors.notes.message}</span> : null}
          </Label>

          <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-600 dark:text-slate-300">Total estimado (visual)</p>
            <p className="text-2xl font-semibold text-slate-900 dark:text-slate-100">${visualTotal.toFixed(2)}</p>
          </div>

          <DialogFooter>
            <Button
              type="button"
              className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
              onClick={() => onOpenChange(false)}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? "Guardando..." : "Crear orden"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
