import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

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
import { Textarea } from "../../../components/ui/textarea";
import {
  categoryRequestSchema,
  type CategoryRequestType,
  type CategoryType,
} from "../types/catalog.types";

type CategoryFormProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialValues?: CategoryType | null;
  isPending: boolean;
  onSubmitCategory: (payload: CategoryRequestType) => Promise<void>;
};

export function CategoryForm({
  open,
  onOpenChange,
  initialValues,
  isPending,
  onSubmitCategory,
}: CategoryFormProps) {
  const isEditing = Boolean(initialValues);
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CategoryRequestType>({
    resolver: zodResolver(categoryRequestSchema),
    defaultValues: {
      name: initialValues?.name ?? "",
      description: initialValues?.description ?? "",
    },
  });

  useEffect(() => {
    reset({
      name: initialValues?.name ?? "",
      description: initialValues?.description ?? "",
    });
  }, [initialValues, reset]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditing ? "Editar categoría" : "Nueva categoría"}</DialogTitle>
          <DialogDescription>
            Completa la información principal de la categoría para el catálogo.
          </DialogDescription>
        </DialogHeader>

        <form
          className="space-y-4"
          onSubmit={handleSubmit(async (data) => {
            await onSubmitCategory(data);
          })}
        >
          <Label className="flex flex-col gap-2">
            Nombre
            <Input placeholder="Bebidas" {...register("name")} />
            {errors.name ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.name.message}</span>
            ) : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Descripción
            <Textarea placeholder="Descripción opcional" {...register("description")} />
            {errors.description ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.description.message}</span>
            ) : null}
          </Label>

          <DialogFooter>
            <Button
              type="button"
              className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
              onClick={() => onOpenChange(false)}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? "Guardando..." : isEditing ? "Guardar cambios" : "Crear categoría"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
