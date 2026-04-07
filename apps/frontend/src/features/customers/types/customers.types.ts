export const dateTimeLikeSchema = z.string().refine((value) => !Number.isNaN(Date.parse(value)), {
  message: "Fecha invalida",
});
import { z } from "zod";

export const customerTypeSchema = z.enum(["persona_natural", "juridica"]);
export type CustomerTypeType = z.infer<typeof customerTypeSchema>;

const validateCedula = (cedula: string): boolean => {
  if (cedula.length !== 10 || !/^\d+$/.test(cedula)) {
    return false;
  }

  const province = Number.parseInt(cedula.slice(0, 2), 10);
  if (province < 1 || province > 24) {
    return false;
  }

  const thirdDigit = Number.parseInt(cedula[2], 10);
  if (thirdDigit >= 6) {
    return false;
  }

  const coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2];
  const total = coefficients.reduce((accumulator, coefficient, index) => {
    let value = Number.parseInt(cedula[index], 10) * coefficient;
    if (value >= 10) {
      value -= 9;
    }
    return accumulator + value;
  }, 0);

  const verifier = total % 10 === 0 ? 0 : 10 - (total % 10);
  return verifier === Number.parseInt(cedula[9], 10);
};

const validateRucPrivateCompany = (ruc: string): boolean => {
  const coefficients = [4, 3, 2, 7, 6, 5, 4, 3, 2];
  const total = coefficients.reduce(
    (accumulator, coefficient, index) => accumulator + Number.parseInt(ruc[index], 10) * coefficient,
    0,
  );
  const remainder = total % 11;
  let verifier = remainder === 0 ? 0 : 11 - remainder;
  if (verifier === 11) {
    verifier = 0;
  }
  return verifier === Number.parseInt(ruc[9], 10);
};

const validateRucPublicEntity = (ruc: string): boolean => {
  const coefficients = [3, 2, 7, 6, 5, 4, 3, 2];
  const total = coefficients.reduce(
    (accumulator, coefficient, index) => accumulator + Number.parseInt(ruc[index], 10) * coefficient,
    0,
  );
  const remainder = total % 11;
  let verifier = remainder === 0 ? 0 : 11 - remainder;
  if (verifier === 11) {
    verifier = 0;
  }
  return verifier === Number.parseInt(ruc[8], 10);
};

const validateRuc = (ruc: string): boolean => {
  if (ruc.length !== 13 || !/^\d+$/.test(ruc)) {
    return false;
  }

  const province = Number.parseInt(ruc.slice(0, 2), 10);
  if (province < 1 || province > 24) {
    return false;
  }

  const establishment = Number.parseInt(ruc.slice(10, 13), 10);
  if (establishment < 1) {
    return false;
  }

  const thirdDigit = Number.parseInt(ruc[2], 10);
  if (thirdDigit < 6) {
    return validateCedula(ruc.slice(0, 10));
  }

  if (thirdDigit === 9) {
    return validateRucPrivateCompany(ruc);
  }

  if (thirdDigit === 6) {
    return validateRucPublicEntity(ruc);
  }

  return false;
};

export const customerRequestSchema = z
  .object({
    name: z.string().min(2, "Minimo 2 caracteres").max(150, "Maximo 150 caracteres"),
    customer_type: customerTypeSchema,
    identification_number: z.string().regex(/^\d+$/, "Solo se permiten digitos"),
    email: z.string().email("Email invalido").optional(),
    phone: z.string().max(20, "Maximo 20 caracteres").optional(),
    address: z.string().max(300, "Maximo 300 caracteres").optional(),
  })
  .superRefine((data, context) => {
    const isValid =
      data.customer_type === "persona_natural"
        ? validateCedula(data.identification_number)
        : validateRuc(data.identification_number);

    if (!isValid) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message:
          data.customer_type === "persona_natural"
            ? "Cedula invalida. Verifique el numero ingresado."
            : "RUC invalido. Verifique el numero ingresado.",
        path: ["identification_number"],
      });
    }
  });
export type CustomerRequestType = z.infer<typeof customerRequestSchema>;

export const customerSchema = z.object({
  id: z.string(),
  name: z.string(),
  customer_type: customerTypeSchema,
  identification_number: z.string(),
  email: z.string().email().nullable(),
  phone: z.string().nullable(),
  address: z.string().nullable(),
  is_active: z.boolean(),
  created_at: dateTimeLikeSchema,
  updated_at: dateTimeLikeSchema,
});
export type CustomerType = z.infer<typeof customerSchema>;

export const customerSearchResultSchema = z.object({
  id: z.string(),
  name: z.string(),
  identification_number: z.string(),
  customer_type: customerTypeSchema,
});
export type CustomerSearchResultType = z.infer<typeof customerSearchResultSchema>;

export const customerListSchema = z.object({
  items: z.array(customerSchema),
  total: z.number().int().nonnegative(),
  skip: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
});
export type CustomerListType = z.infer<typeof customerListSchema>;
