import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

import { Button } from "../../../components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "../../../components/ui/dialog";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { stockInitRequestSchema, type StockInitRequestType } from "../types/inventory.types";

type StockInitFormProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  productName: string;
  isPending: boolean;
  onSubmitInit: (payload: StockInitRequestType) => Promise<void>;
};

export function StockInitForm({ open, onOpenChange, productName, isPending, onSubmitInit }: StockInitFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<StockInitRequestType>({
    resolver: zodResolver(stockInitRequestSchema),
    defaultValues: {
      quantity: 0,
      min_stock: 0,
    },
  });

  useEffect(() => {
    if (!open) {
      reset({ quantity: 0, min_stock: 0 });
    }
  }, [open, reset]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Inicializar stock</DialogTitle>
          <DialogDescription>Define stock inicial y umbral minimo para {productName}.</DialogDescription>
        </DialogHeader>

        <form
          className="space-y-4"
          onSubmit={handleSubmit(async (payload) => {
            await onSubmitInit(payload);
          })}
        >
          <Label className="flex flex-col gap-2">
            Cantidad inicial
            <Input type="number" min={0} step={1} {...register("quantity", { valueAsNumber: true })} />
            {errors.quantity ? <span className="text-sm text-red-600 dark:text-red-400">{errors.quantity.message}</span> : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Stock mínimo
            <Input type="number" min={0} step={1} {...register("min_stock", { valueAsNumber: true })} />
            {errors.min_stock ? <span className="text-sm text-red-600 dark:text-red-400">{errors.min_stock.message}</span> : null}
          </Label>

          <DialogFooter>
            <Button type="button" className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending}>{isPending ? "Guardando..." : "Inicializar"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
