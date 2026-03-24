import { z } from "zod";

export const roleSchema = z.enum(["admin", "vendedor", "bodeguero"]);
export type RoleType = z.infer<typeof roleSchema>;

export const registerSchema = z.object({
  email: z.string().email("Correo electrónico inválido"),
  password: z
    .string()
    .min(8, "Mínimo 8 caracteres")
    .regex(/[A-Z]/, "Debe contener al menos una mayúscula")
    .regex(/[0-9]/, "Debe contener al menos un número"),
  full_name: z.string().min(2, "Mínimo 2 caracteres").max(100, "Máximo 100 caracteres"),
});
export type RegisterType = z.infer<typeof registerSchema>;

export const loginSchema = z.object({
  email: z.string().email("Correo electrónico inválido"),
  password: z.string().min(1, "La contraseña es requerida"),
});
export type LoginType = z.infer<typeof loginSchema>;

export const userSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  full_name: z.string(),
  role: roleSchema,
  is_active: z.boolean(),
  created_at: z.string().refine((value) => !Number.isNaN(Date.parse(value)), {
    message: "Fecha inválida",
  }),
});
export type UserType = z.infer<typeof userSchema>;

export const tokenResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.literal("bearer"),
});
export type TokenResponseType = z.infer<typeof tokenResponseSchema>;
