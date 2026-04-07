import { describe, expect, it } from "vitest";

import { customerRequestSchema } from "./customers.types";

describe("customerRequestSchema", () => {
  it("should_reject_cedula_with_invalid_verifier_in_zod_schema", () => {
    const parsed = customerRequestSchema.safeParse({
      name: "Cliente Uno",
      customer_type: "persona_natural",
      identification_number: "1710034066",
    });

    expect(parsed.success).toBe(false);
  });

  it("should_accept_valid_cedula_in_zod_schema", () => {
    const parsed = customerRequestSchema.safeParse({
      name: "Cliente Uno",
      customer_type: "persona_natural",
      identification_number: "1710034065",
    });

    expect(parsed.success).toBe(true);
  });

  it("should_reject_ruc_with_invalid_format_in_zod_schema", () => {
    const parsed = customerRequestSchema.safeParse({
      name: "Comercial ABC",
      customer_type: "juridica",
      identification_number: "1790012345000",
    });

    expect(parsed.success).toBe(false);
  });
});
