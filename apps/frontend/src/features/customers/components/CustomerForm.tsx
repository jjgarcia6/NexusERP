import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

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
import {
  customerRequestSchema,
  type CustomerRequestType,
  type CustomerType,
} from "../types/customers.types";

type CustomerFormProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialValues?: CustomerType | null;
  isPending: boolean;
  submitError?: string | null;
  onSubmitCreate: (payload: CustomerRequestType) => Promise<void>;
  onSubmitUpdate: (payload: {
    name?: string;
    email?: string;
    phone?: string;
    address?: string;
  }) => Promise<void>;
};

const customerUpdateSchema = z.object({
  name: z.string().min(2, "Minimo 2 caracteres").max(150, "Maximo 150 caracteres").optional(),
  email: z.string().email("Email invalido").optional(),
  phone: z.string().max(20, "Maximo 20 caracteres").optional(),
  address: z.string().max(300, "Maximo 300 caracteres").optional(),
});

type CustomerFormValues = {
  name: string;
  customer_type: "persona_natural" | "juridica";
  identification_number: string;
  email: string;
  phone: string;
  address: string;
};

function toOptionalString(value: string): string | undefined {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

export function CustomerForm({
  open,
  onOpenChange,
  initialValues,
  isPending,
  submitError,
  onSubmitCreate,
  onSubmitUpdate,
}: CustomerFormProps) {
  const isEditing = Boolean(initialValues);
  const {
    register,
    watch,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CustomerFormValues>({
    resolver: zodResolver(customerRequestSchema),
    defaultValues: {
      name: initialValues?.name ?? "",
      customer_type: initialValues?.customer_type ?? "persona_natural",
      identification_number: initialValues?.identification_number ?? "",
      email: initialValues?.email ?? "",
      phone: initialValues?.phone ?? "",
      address: initialValues?.address ?? "",
    },
  });

  useEffect(() => {
    reset({
      name: initialValues?.name ?? "",
      customer_type: initialValues?.customer_type ?? "persona_natural",
      identification_number: initialValues?.identification_number ?? "",
      email: initialValues?.email ?? "",
      phone: initialValues?.phone ?? "",
      address: initialValues?.address ?? "",
    });
  }, [initialValues, reset]);

  const customerType = watch("customer_type");
  const identificationPlaceholder =
    customerType === "persona_natural" ? "Ej: 1712345678" : "Ej: 1712345678001";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Editar cliente" : "Nuevo cliente"}</DialogTitle>
          <DialogDescription>
            Registra datos de cliente para facturacion y seleccion en el POS.
          </DialogDescription>
        </DialogHeader>

        <form
          className="grid grid-cols-1 gap-4 md:grid-cols-2"
          onSubmit={handleSubmit(async (data) => {
            if (isEditing) {
              const parsedUpdate = customerUpdateSchema.parse({
                name: toOptionalString(data.name),
                email: toOptionalString(data.email),
                phone: toOptionalString(data.phone),
                address: toOptionalString(data.address),
              });
              await onSubmitUpdate(parsedUpdate);
              return;
            }

            const parsedCreate = customerRequestSchema.parse({
              name: data.name,
              customer_type: data.customer_type,
              identification_number: data.identification_number,
              email: toOptionalString(data.email),
              phone: toOptionalString(data.phone),
              address: toOptionalString(data.address),
            });
            await onSubmitCreate(parsedCreate);
          })}
        >
          <Label className="flex flex-col gap-2 md:col-span-2">
            Nombre o razon social
            <Input placeholder="Comercial XYZ" {...register("name")} />
            {errors.name ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.name.message}</span>
            ) : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Tipo de cliente
            <Select {...register("customer_type")} disabled={isEditing}>
              <option value="persona_natural">Persona natural</option>
              <option value="juridica">Juridica</option>
            </Select>
            {errors.customer_type ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.customer_type.message}</span>
            ) : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Identificacion
            <Input
              placeholder={identificationPlaceholder}
              {...register("identification_number")}
              disabled={isEditing}
            />
            {errors.identification_number ? (
              <span className="text-sm text-red-600 dark:text-red-400">
                {errors.identification_number.message}
              </span>
            ) : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Email
            <Input type="email" placeholder="cliente@dominio.com" {...register("email")} />
            {errors.email ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.email.message}</span>
            ) : null}
          </Label>

          <Label className="flex flex-col gap-2">
            Telefono
            <Input placeholder="0999999999" {...register("phone")} />
            {errors.phone ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.phone.message}</span>
            ) : null}
          </Label>

          <Label className="flex flex-col gap-2 md:col-span-2">
            Direccion
            <Input placeholder="Av. Principal 123" {...register("address")} />
            {errors.address ? (
              <span className="text-sm text-red-600 dark:text-red-400">{errors.address.message}</span>
            ) : null}
          </Label>

          {submitError ? (
            <p className="md:col-span-2 text-sm text-red-600 dark:text-red-400">{submitError}</p>
          ) : null}

          <DialogFooter className="md:col-span-2">
            <Button
              type="button"
              className="bg-slate-200 text-slate-900 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-100 dark:hover:bg-slate-600"
              onClick={() => onOpenChange(false)}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? "Guardando..." : isEditing ? "Guardar cambios" : "Crear cliente"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
