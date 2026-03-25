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
import {
  supplierRequestSchema,
  type SupplierRequestType,
  type SupplierType,
} from "../types/purchases.types";

type SupplierFormProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialValues?: SupplierType | null;
  isPending: boolean;
  onSubmitSupplier: (payload: SupplierRequestType) => Promise<void>;
};

function toOptionalString(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }

  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

export function SupplierForm({
  open,
  onOpenChange,
  initialValues,
  isPending,
  onSubmitSupplier,
}: SupplierFormProps) {
  const isEditing = Boolean(initialValues);
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<SupplierRequestType>({
    resolver: zodResolver(supplierRequestSchema),
    defaultValues: {
      name: initialValues?.name ?? "",
      ruc: initialValues?.ruc ?? undefined,
      contact_name: initialValues?.contact_name ?? undefined,
      contact_email: initialValues?.contact_email ?? undefined,
      contact_phone: initialValues?.contact_phone ?? undefined,
      address: initialValues?.address ?? undefined,
    },
  });

  useEffect(() => {
    reset({
      name: initialValues?.name ?? "",
      ruc: initialValues?.ruc ?? undefined,
      contact_name: initialValues?.contact_name ?? undefined,
      contact_email: initialValues?.contact_email ?? undefined,
      contact_phone: initialValues?.contact_phone ?? undefined,
      address: initialValues?.address ?? undefined,
    });
  }, [initialValues, reset]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Editar proveedor" : "Nuevo proveedor"}</DialogTitle>
          <DialogDescription>
            Completa los datos del proveedor para crear o actualizar su ficha de compras.
          </DialogDescription>
        </DialogHeader>

        <form
          className="grid grid-cols-1 gap-4 md:grid-cols-2"
          onSubmit={handleSubmit(async (data) => {
            await onSubmitSupplier(data);
          })}
        >
          <Label className="col-span-1 flex flex-col gap-2 md:col-span-2">
            Nombre
            <Input placeholder="Proveedor ABC S.A." {...register("name")} />
            {errors.name ? <span className="text-sm text-red-600 dark:text-red-400">{errors.name.message}</span> : null}
          </Label>

          <Label className="flex flex-col gap-2">
            RUC
            <Input
              placeholder="1790012345001"
              {...register("ruc", {
                setValueAs: toOptionalString,
              })}
            />
            {errors.ruc ? <span className="text-sm text-red-600 dark:text-red-400">{errors.ruc.message}</span> : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Nombre de contacto
            <Input
              placeholder="María Pérez"
              {...register("contact_name", {
                setValueAs: toOptionalString,
              })}
            />
            {errors.contact_name ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.contact_name.message}</span>
            ) : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Correo de contacto
            <Input
              type="email"
              placeholder="contacto@proveedor.com"
              {...register("contact_email", {
                setValueAs: toOptionalString,
              })}
            />
            {errors.contact_email ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.contact_email.message}</span>
            ) : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Teléfono de contacto
            <Input
              placeholder="0999999999"
              {...register("contact_phone", {
                setValueAs: toOptionalString,
              })}
            />
            {errors.contact_phone ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.contact_phone.message}</span>
            ) : null}
          </Label>

          <Label className="col-span-1 flex flex-col gap-2 md:col-span-2">
            Dirección
            <Input
              placeholder="Av. Principal 123 y Calle Secundaria"
              {...register("address", {
                setValueAs: toOptionalString,
              })}
            />
            {errors.address ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.address.message}</span>
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
              {isPending ? "Guardando..." : isEditing ? "Guardar cambios" : "Crear proveedor"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
