import { z } from "zod";

export const healthSchema = z.object({
  status: z.literal("ok"),
});

export type HealthType = z.infer<typeof healthSchema>;

export const serviceUnavailableSchema = z.object({
  status: z.literal("error"),
  detail: z.literal("database unavailable"),
});

export type ServiceUnavailableType = z.infer<typeof serviceUnavailableSchema>;
