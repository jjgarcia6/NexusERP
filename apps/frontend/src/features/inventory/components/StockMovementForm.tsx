import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

import { Button } from "../../../components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "../../../components/ui/dialog";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select } from "../../../components/ui/select";
import { Textarea } from "../../../components/ui/textarea";
import { manualMovementTypes, stockMovementRequestSchema, type StockLevelType, type StockMovementRequestType } from "../types/inventory.types";

type StockMovementFormProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  products: StockLevelType[];
  defaultProductId?: string;
  isPending: boolean;
  onSubmitMovement: (payload: StockMovementRequestType) => Promise<void>;
};

export function StockMovementForm({
  open,
  onOpenChange,
  products,
  defaultProductId,
  isPending,
  onSubmitMovement,
}: StockMovementFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<StockMovementRequestType>({
    resolver: zodResolver(stockMovementRequestSchema),
    defaultValues: {
      product_id: defaultProductId ?? "",
      type: "manual_entry",
      quantity: 1,
      reason: "",
    },
  });

  useEffect(() => {
    if (open) {
      reset({
        product_id: defaultProductId ?? "",
        type: "manual_entry",
        quantity: 1,
        reason: "",
      });
    }
  }, [defaultProductId, open, reset]);

  const selectedProduct = products.find((product) => product.product_id === watch("product_id"));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Registrar movimiento</DialogTitle>
          <DialogDescription>Registra entradas, salidas o ajustes manuales de stock.</DialogDescription>
        </DialogHeader>

        <form
          className="space-y-4"
          onSubmit={handleSubmit(async (payload) => {
            await onSubmitMovement(payload);
          })}
        >
          <Label className="flex flex-col gap-2">
            Producto
            <Select {...register("product_id")}>
              <option value="">Seleccione</option>
              {products.map((product) => (
                <option key={product.product_id} value={product.product_id}>
                  {product.product_name}
                </option>
              ))}
            </Select>
            {selectedProduct ? (
              <span className="text-xs text-slate-600 dark:text-slate-300">Stock actual: {selectedProduct.available_quantity}</span>
            ) : null}
            {errors.product_id ? <span className="text-sm text-red-600 dark:text-red-400">{errors.product_id.message}</span> : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Tipo
            <Select {...register("type")}>
              {manualMovementTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </Select>
            {errors.type ? <span className="text-sm text-red-600 dark:text-red-400">{errors.type.message}</span> : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Cantidad
            <Input type="number" step={1} {...register("quantity", { valueAsNumber: true })} />
            {errors.quantity ? <span className="text-sm text-red-600 dark:text-red-400">{errors.quantity.message}</span> : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Motivo
            <Textarea rows={3} {...register("reason")} />
            {errors.reason ? <span className="text-sm text-red-600 dark:text-red-400">{errors.reason.message}</span> : null}
          </Label>

          <DialogFooter>
            <Button type="button" className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending}>{isPending ? "Guardando..." : "Registrar"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
