import { z } from "zod";

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

export const categorySchema = z.preprocess(
  normalizeMongoId,
  z.object({
    id: z.string(),
    _id: objectIdSchema.optional(),
    name: z.string().min(2).max(80),
    description: z.string().max(300).nullable().optional(),
    is_active: z.boolean(),
    created_at: dateTimeLikeSchema,
    updated_at: dateTimeLikeSchema,
  }),
);
export type CategoryType = z.infer<typeof categorySchema>;

export const categoryRequestSchema = z.object({
  name: z.string().min(2, "Minimo 2 caracteres").max(80, "Maximo 80 caracteres"),
  description: z.string().max(300).optional(),
});
export type CategoryRequestType = z.infer<typeof categoryRequestSchema>;

export const productSchema = z.preprocess(
  normalizeMongoId,
  z.object({
    id: z.string(),
    _id: objectIdSchema.optional(),
    name: z.string().min(2).max(150),
    description: z.string().max(1000).nullable().optional(),
    sku: z.string().max(50).nullable().optional(),
    price: z.coerce.number().positive(),
    cost: z.coerce.number().positive().nullable().optional(),
    category_id: z.string(),
    category_name: z.string(),
    image_url: z.string().url().max(500).nullable().optional(),
    min_stock: z.number().int().nonnegative().default(0),
    is_active: z.boolean(),
    created_at: dateTimeLikeSchema,
    updated_at: dateTimeLikeSchema,
  }),
);
export type ProductType = z.infer<typeof productSchema>;

export const productRequestSchema = z.object({
  name: z.string().min(2, "Minimo 2 caracteres").max(150, "Maximo 150 caracteres"),
  description: z.string().max(1000).optional(),
  sku: z.string().max(50).optional(),
  price: z
    .number({ invalid_type_error: "El precio debe ser un numero" })
    .positive("El precio debe ser mayor a 0"),
  cost: z.number().positive().optional(),
  category_id: z.string().min(1, "Seleccione una categoria"),
  image_url: z.string().url("URL invalida").max(500).optional(),
  min_stock: z.number().int().nonnegative().default(0),
});
export type ProductRequestType = z.infer<typeof productRequestSchema>;

export const productListSchema = z.object({
  items: z.array(productSchema),
  total: z.number().int().nonnegative(),
  skip: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
});
export type ProductListType = z.infer<typeof productListSchema>;
