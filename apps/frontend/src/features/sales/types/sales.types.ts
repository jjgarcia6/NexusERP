import { z } from "zod";

export const saleStatusSchema = z.enum(["draft", "confirmed", "cancelled"]);
export type SaleStatusType = z.infer<typeof saleStatusSchema>;

export const paymentMethodSchema = z.enum(["cash", "card", "transfer"]);
export type PaymentMethodType = z.infer<typeof paymentMethodSchema>;

const numericSchema = z.coerce.number();

export const saleLineRequestSchema = z.object({
  product_id: z.string().min(1, "Seleccione un producto"),
  quantity: z.number({ invalid_type_error: "Debe ser un número" })
    .int("Debe ser un entero")
    .positive("Debe ser mayor a 0"),
});
export type SaleLineRequestType = z.infer<typeof saleLineRequestSchema>;

export const saleRequestSchema = z.object({
  customer_id: z.string().min(1, "Seleccione un cliente"),
  payment_method: paymentMethodSchema,
  lines: z.array(saleLineRequestSchema)
    .min(1, "La venta debe tener al menos una línea de producto"),
  notes: z.string().max(500).optional(),
});
export type SaleRequestType = z.infer<typeof saleRequestSchema>;

export const saleLineResponseSchema = z.object({
  product_id: z.string(),
  product_name: z.string(),
  quantity: numericSchema.int().positive(),
  unit_price: numericSchema.positive(),
  subtotal: numericSchema.positive(),
});
export type SaleLineResponseType = z.infer<typeof saleLineResponseSchema>;

export const saleSchema = z.object({
  id: z.string(),
  customer_id: z.string(),
  customer_name: z.string(),
  customer_identification: z.string(),
  status: saleStatusSchema,
  invoice_number: z.string().nullable(),
  payment_method: paymentMethodSchema,
  lines: z.array(saleLineResponseSchema),
  subtotal_before_tax: numericSchema,
  tax_rate: numericSchema,
  tax_amount: numericSchema,
  total: numericSchema,
  notes: z.string().nullable(),
  confirmed_at: z.string().datetime().nullable(),
  cancelled_at: z.string().datetime().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});
export type SaleType = z.infer<typeof saleSchema>;

export const saleListSchema = z.object({
  items: z.array(saleSchema),
  total: z.number().int().nonnegative(),
  skip: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
});
export type SaleListType = z.infer<typeof saleListSchema>;

export const cartLineSchema = z.object({
  product_id: z.string(),
  product_name: z.string(),
  unit_price: z.number(),
  available_quantity: z.number().int().nonnegative(),
  quantity: z.number().int().positive(),
});
export type CartLineType = z.infer<typeof cartLineSchema>;
