import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";

import apiClient from "../../../shared/api/client";
import {
  supplierRequestSchema,
  supplierSchema,
  type SupplierRequestType,
  type SupplierType,
} from "../types/purchases.types";

type UseSuppliersResult = {
  suppliers: SupplierType[];
  isLoading: boolean;
  errorMessage: string | null;
  createSupplier: (payload: SupplierRequestType) => Promise<SupplierType>;
  updateSupplier: (params: {
    supplierId: string;
    payload: Partial<SupplierRequestType> & { is_active?: boolean };
  }) => Promise<SupplierType>;
};

export function useSuppliers(): UseSuppliersResult {
  const queryClient = useQueryClient();

  const suppliersQuery = useQuery({
    queryKey: ["suppliers"],
    queryFn: async () => {
      const response = await apiClient.get("/suppliers");
      const rawItems = Array.isArray(response.data)
        ? response.data
        : Array.isArray((response.data as { items?: unknown }).items)
          ? (response.data as { items: unknown[] }).items
          : [];
      return supplierSchema.array().parse(rawItems);
    },
  });

  const createSupplierMutation = useMutation({
    mutationFn: async (payload: SupplierRequestType) => {
      const parsedPayload = supplierRequestSchema.parse(payload);
      const response = await apiClient.post("/suppliers", parsedPayload);
      return supplierSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["suppliers"] });
    },
  });

  const updateSupplierMutation = useMutation({
    mutationFn: async (params: {
      supplierId: string;
      payload: Partial<SupplierRequestType> & { is_active?: boolean };
    }) => {
      // Create update schema without relying on .partial() on a ZodEffects type
      const updateSchema = z.object({
        name: z.string().min(2).max(150).optional(),
        ruc: z.string().max(13).nullable().optional(),
        contact_name: z.string().max(100).nullable().optional(),
        contact_email: z.string().email().nullable().optional(),
        contact_phone: z.string().max(20).nullable().optional(),
        address: z.string().max(300).nullable().optional(),
        is_active: z.boolean().optional(),
      });
      const parsedPayload = updateSchema.parse(params.payload);
      const response = await apiClient.patch(`/suppliers/${params.supplierId}`, parsedPayload);
      return supplierSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["suppliers"] });
    },
  });

  return {
    suppliers: suppliersQuery.data ?? [],
    isLoading: suppliersQuery.isLoading,
    errorMessage: suppliersQuery.isError ? "No fue posible cargar proveedores." : null,
    createSupplier: createSupplierMutation.mutateAsync,
    updateSupplier: updateSupplierMutation.mutateAsync,
  };
}
