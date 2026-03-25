import { z } from "zod";

export const orderStatusSchema = z.enum(["draft", "confirmed", "received", "cancelled"]);
export type OrderStatusType = z.infer<typeof orderStatusSchema>;

const dateTimeLikeSchema = z.string().refine((value) => !Number.isNaN(Date.parse(value)), {
  message: "Fecha invalida",
});

const objectIdSchema = z.union([
  z.string(),
  z.object({
    $oid: z.string(),
  }),
]);

const normalizeMongoId = (value: unknown): unknown => {
  if (!value || typeof value !== "object") {
    return value;
  }

  const record = value as Record<string, unknown>;
  if (typeof record.id === "string") {
    return value;
  }

  if (typeof record._id === "string") {
    return { ...record, id: record._id };
  }

  if (record._id && typeof record._id === "object") {
    const objectId = record._id as Record<string, unknown>;
    if (typeof objectId.$oid === "string") {
      return { ...record, id: objectId.$oid };
    }
  }

  return value;
};

export const supplierSchema = z.preprocess(
  normalizeMongoId,
  z.object({
    id: z.string(),
    _id: objectIdSchema.optional(),
    name: z.string().min(2).max(150),
    ruc: z.string().max(13).nullable().optional(),
    contact_name: z.string().max(100).nullable().optional(),
    contact_email: z.string().email().nullable().optional(),
    contact_phone: z.string().max(20).nullable().optional(),
    address: z.string().max(300).nullable().optional(),
    is_active: z.boolean(),
    created_at: dateTimeLikeSchema,
    updated_at: dateTimeLikeSchema,
  }),
);
export type SupplierType = z.infer<typeof supplierSchema>;

export const supplierRequestSchema = z.object({
  name: z.string().min(2, "Minimo 2 caracteres").max(150, "Maximo 150 caracteres"),
  ruc: z.string().max(13).nullable().optional(),
  contact_name: z.string().max(100).nullable().optional(),
  contact_email: z.string().email("Email invalido").nullable().optional(),
  contact_phone: z.string().max(20).nullable().optional(),
  address: z.string().max(300).nullable().optional(),
});
export type SupplierRequestType = z.infer<typeof supplierRequestSchema>;

export const purchaseOrderLineRequestSchema = z.object({
  product_id: z.string().min(1, "Seleccione un producto"),
  quantity: z
    .number({ invalid_type_error: "Debe ser un numero" })
    .int("Debe ser un numero entero")
    .positive("Debe ser mayor a 0"),
  unit_cost: z
    .number({ invalid_type_error: "Debe ser un numero" })
    .positive("Debe ser mayor a 0"),
});
export type PurchaseOrderLineRequestType = z.infer<typeof purchaseOrderLineRequestSchema>;

export const purchaseOrderLineResponseSchema = purchaseOrderLineRequestSchema.extend({
  unit_cost: z.coerce.number().positive(),
  product_name: z.string(),
  subtotal: z.coerce.number().positive(),
});
export type PurchaseOrderLineResponseType = z.infer<typeof purchaseOrderLineResponseSchema>;

export const purchaseOrderRequestSchema = z.object({
  supplier_id: z.string().min(1, "Seleccione un proveedor"),
  lines: z
    .array(purchaseOrderLineRequestSchema)
    .min(1, "La orden debe tener al menos una linea de producto"),
  notes: z.string().max(500).optional(),
});
export type PurchaseOrderRequestType = z.infer<typeof purchaseOrderRequestSchema>;

export const purchaseOrderSchema = z.object({
  id: z.string(),
  supplier_id: z.string(),
  supplier_name: z.string(),
  status: orderStatusSchema,
  lines: z.array(purchaseOrderLineResponseSchema),
  total: z.coerce.number().positive(),
  notes: z.string().nullable(),
  confirmed_at: dateTimeLikeSchema.nullable(),
  received_at: dateTimeLikeSchema.nullable(),
  cancelled_at: dateTimeLikeSchema.nullable(),
  created_at: dateTimeLikeSchema,
  updated_at: dateTimeLikeSchema,
});
export type PurchaseOrderType = z.infer<typeof purchaseOrderSchema>;

export const purchaseOrderListSchema = z.object({
  items: z.array(purchaseOrderSchema),
  total: z.number().int().nonnegative(),
  skip: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
});
export type PurchaseOrderListType = z.infer<typeof purchaseOrderListSchema>;
