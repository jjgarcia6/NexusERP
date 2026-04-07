import { z } from "zod";

export const granularitySchema = z.enum(["day", "week", "month"]);
export type GranularityType = z.infer<typeof granularitySchema>;

export const periodPresetSchema = z.enum([
  "today",
  "last7days",
  "last30days",
  "thisMonth",
  "custom",
]);
export type PeriodPresetType = z.infer<typeof periodPresetSchema>;

export const periodRangeSchema = z.object({
  from: z.string().datetime(),
  to: z.string().datetime(),
});
export type PeriodRange = z.infer<typeof periodRangeSchema>;

const numericSchema = z.coerce.number();

export const topProductSchema = z.object({
  product_id: z.string(),
  product_name: z.string(),
  total_quantity: z.number().int().nonnegative(),
  total_amount: numericSchema.nonnegative(),
});
export type TopProductType = z.infer<typeof topProductSchema>;

export const topCustomerSchema = z.object({
  customer_name: z.string(),
  identification_masked: z.string(),
  total_purchases: z.number().int().nonnegative(),
  total_amount: numericSchema.nonnegative(),
});
export type TopCustomerType = z.infer<typeof topCustomerSchema>;

export const dashboardSchema = z.object({
  total_sales_amount: numericSchema.nonnegative(),
  total_transactions: z.number().int().nonnegative(),
  average_ticket: numericSchema.nonnegative(),
  top_products: z.array(topProductSchema),
  top_customers: z.array(topCustomerSchema),
  low_stock_count: z.number().int().nonnegative(),
  period_from: z.string().datetime(),
  period_to: z.string().datetime(),
});
export type DashboardType = z.infer<typeof dashboardSchema>;

export const salesReportEntrySchema = z.object({
  date: z.string(),
  transactions: z.number().int().nonnegative(),
  subtotal_before_tax: numericSchema.nonnegative(),
  tax_amount: numericSchema.nonnegative(),
  total: numericSchema.nonnegative(),
});
export type SalesReportEntryType = z.infer<typeof salesReportEntrySchema>;

export const salesReportSchema = z.object({
  entries: z.array(salesReportEntrySchema),
  grand_total: numericSchema.nonnegative(),
  total_transactions: z.number().int().nonnegative(),
});
export type SalesReportType = z.infer<typeof salesReportSchema>;

export const inventoryReportEntrySchema = z.object({
  product_id: z.string(),
  product_name: z.string(),
  available_quantity: z.number().int().nonnegative(),
  unit_cost: numericSchema.nonnegative(),
  total_value: numericSchema.nonnegative(),
  low_stock: z.boolean(),
  units_sold: z.number().int().nonnegative(),
  rotation_rate: numericSchema.nonnegative(),
});
export type InventoryReportEntryType = z.infer<typeof inventoryReportEntrySchema>;

export const inventoryReportSchema = z.object({
  entries: z.array(inventoryReportEntrySchema),
  grand_total_value: numericSchema.nonnegative(),
});
export type InventoryReportType = z.infer<typeof inventoryReportSchema>;

export const customerReportEntrySchema = z.object({
  customer_name: z.string(),
  identification_masked: z.string(),
  total_purchases: z.number().int().nonnegative(),
  total_amount: numericSchema.nonnegative(),
  last_purchase_at: z.string().datetime(),
});
export type CustomerReportEntryType = z.infer<typeof customerReportEntrySchema>;

export const customerReportSchema = z.object({
  entries: z.array(customerReportEntrySchema),
  period_from: z.string().datetime(),
  period_to: z.string().datetime(),
});
export type CustomerReportType = z.infer<typeof customerReportSchema>;

export const purchasesReportEntrySchema = z.object({
  supplier_name: z.string(),
  total_orders: z.number().int().nonnegative(),
  total_amount: numericSchema.nonnegative(),
  last_order_at: z.string().datetime(),
});
export type PurchasesReportEntryType = z.infer<typeof purchasesReportEntrySchema>;

export const purchasesReportSchema = z.object({
  entries: z.array(purchasesReportEntrySchema),
  grand_total: numericSchema.nonnegative(),
});
export type PurchasesReportType = z.infer<typeof purchasesReportSchema>;
