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
import { Select } from "../../../components/ui/select";
import { Textarea } from "../../../components/ui/textarea";
import {
  productRequestSchema,
  type CategoryType,
  type ProductRequestType,
  type ProductType,
} from "../types/catalog.types";

type ProductFormValues = ProductRequestType;

type ProductFormProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialValues?: ProductType | null;
  categories: CategoryType[];
  isAdmin: boolean;
  isPending: boolean;
  onSubmitProduct: (payload: ProductRequestType) => Promise<void>;
};

export function ProductForm({
  open,
  onOpenChange,
  initialValues,
  categories,
  isAdmin,
  isPending,
  onSubmitProduct,
}: ProductFormProps) {
  const isEditing = Boolean(initialValues);
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProductFormValues>({
    resolver: zodResolver(productRequestSchema),
    defaultValues: {
      name: initialValues?.name ?? "",
      sku: initialValues?.sku ?? "",
      price: initialValues?.price ?? 0,
      cost: initialValues?.cost ?? undefined,
      category_id: initialValues?.category_id ?? "",
      description: initialValues?.description ?? "",
      image_url: initialValues?.image_url ?? "",
    },
  });

  useEffect(() => {
    reset({
      name: initialValues?.name ?? "",
      sku: initialValues?.sku ?? "",
      price: initialValues?.price ?? 0,
      cost: initialValues?.cost ?? undefined,
      category_id: initialValues?.category_id ?? "",
      description: initialValues?.description ?? "",
      image_url: initialValues?.image_url ?? "",
    });
  }, [initialValues, reset]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Editar producto" : "Nuevo producto"}</DialogTitle>
          <DialogDescription>Completa los datos principales del producto del catálogo.</DialogDescription>
        </DialogHeader>

        <form
          className="grid grid-cols-1 gap-4 md:grid-cols-2"
          onSubmit={handleSubmit(async (data) => {
            await onSubmitProduct(data);
          })}
        >
          <Label className="flex flex-col gap-2">
            Nombre
            <Input placeholder="Agua mineral 500ml" {...register("name")} />
            {errors.name ? <span className="text-sm text-red-600 dark:text-red-400">{errors.name.message}</span> : null}
          </Label>

          <Label className="flex flex-col gap-2">
            SKU
            <Input placeholder="SKU-001" {...register("sku")} />
            {errors.sku ? <span className="text-sm text-red-600 dark:text-red-400">{errors.sku.message}</span> : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Precio
            <Input
              type="number"
              step="0.01"
              min="0"
              {...register("price", { valueAsNumber: true })}
            />
            {errors.price ? <span className="text-sm text-red-600 dark:text-red-400">{errors.price.message}</span> : null}
          </Label>

          {isAdmin ? (
            <Label className="flex flex-col gap-2">
              Costo
              <Input
                type="number"
                step="0.01"
                min="0"
                {...register("cost", {
                  setValueAs: (value) => (value === "" ? undefined : Number(value)),
                })}
              />
              {errors.cost ? <span className="text-sm text-red-600 dark:text-red-400">{errors.cost.message}</span> : null}
            </Label>
          ) : null}

          <Label className="flex flex-col gap-2">
            Categoría
            <Select {...register("category_id")}>
              <option value="">Seleccione una categoría</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </Select>
            {errors.category_id ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.category_id.message}</span>
            ) : null}
          </Label>

          <Label className="flex flex-col gap-2">
            URL de imagen
            <Input placeholder="https://..." {...register("image_url")} />
            {errors.image_url ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.image_url.message}</span>
            ) : null}
          </Label>

          <Label className="col-span-1 flex flex-col gap-2 md:col-span-2">
            Descripción
            <Textarea placeholder="Descripción opcional" {...register("description")} />
            {errors.description ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.description.message}</span>
            ) : null}
          </Label>

          <DialogFooter className="col-span-1 md:col-span-2">
            <Button
              type="button"
              className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
              onClick={() => onOpenChange(false)}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? "Guardando..." : isEditing ? "Guardar cambios" : "Crear producto"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
