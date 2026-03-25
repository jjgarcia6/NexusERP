import { z } from "zod";

export const movementTypeSchema = z.enum([
  "purchase_entry",
  "sale_exit",
  "manual_entry",
  "manual_exit",
  "adjustment",
]);
export type MovementTypeType = z.infer<typeof movementTypeSchema>;

export const manualMovementTypes = ["manual_entry", "manual_exit", "adjustment"] as const satisfies MovementTypeType[];

export const stockLevelSchema = z.object({
  product_id: z.string(),
  product_name: z.string(),
  available_quantity: z.number().int().nonnegative(),
  min_stock: z.number().int().nonnegative(),
  low_stock: z.boolean(),
  updated_at: z.string().datetime(),
});
export type StockLevelType = z.infer<typeof stockLevelSchema>;

export const stockListSchema = z.object({
  items: z.array(stockLevelSchema),
  total: z.number().int().nonnegative(),
  skip: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
});
export type StockListType = z.infer<typeof stockListSchema>;

export const stockInitRequestSchema = z.object({
  quantity: z.coerce.number().int().nonnegative(),
  min_stock: z.coerce.number().int().nonnegative().default(0),
});
export type StockInitRequestType = z.infer<typeof stockInitRequestSchema>;

export const stockMovementRequestSchema = z.object({
  product_id: z.string().min(1, "Seleccione un producto"),
  type: z.enum(["manual_entry", "manual_exit", "adjustment"]),
  quantity: z.coerce
    .number()
    .int()
    .refine((value) => value !== 0, "La cantidad no puede ser cero"),
  reason: z.string().min(5, "El motivo debe tener al menos 5 caracteres").max(300, "Maximo 300 caracteres"),
});
export type StockMovementRequestType = z.infer<typeof stockMovementRequestSchema>;

export const stockMovementSchema = z.object({
  id: z.string(),
  product_id: z.string(),
  product_name: z.string(),
  type: movementTypeSchema,
  quantity: z.number().int(),
  quantity_before: z.number().int().nonnegative(),
  quantity_after: z.number().int().nonnegative(),
  reason: z.string().nullable(),
  reference_id: z.string().nullable(),
  reference_type: z.string().nullable(),
  created_at: z.string().datetime(),
});
export type StockMovementType = z.infer<typeof stockMovementSchema>;

export const stockMovementListSchema = z.object({
  items: z.array(stockMovementSchema),
  total: z.number().int().nonnegative(),
  skip: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
});
export type StockMovementListType = z.infer<typeof stockMovementListSchema>;
