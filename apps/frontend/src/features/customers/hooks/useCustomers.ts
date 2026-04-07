import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";

import apiClient from "../../../shared/api/client";
import {
  customerListSchema,
  customerRequestSchema,
  customerSchema,
  type CustomerListType,
  type CustomerRequestType,
  type CustomerType,
} from "../types/customers.types";

type UseCustomersParams = {
  search?: string;
  skip?: number;
  limit?: number;
};

type UseCustomersResult = {
  customers: CustomerType[];
  total: number;
  isLoading: boolean;
  createCustomer: (payload: CustomerRequestType) => Promise<CustomerType>;
  updateCustomer: (params: {
    customerId: string;
    payload: Partial<Omit<CustomerRequestType, "customer_type" | "identification_number">> & {
      is_active?: boolean;
    };
  }) => Promise<CustomerType>;
};

export function useCustomers(params: UseCustomersParams): UseCustomersResult {
  const queryClient = useQueryClient();

  const customersQuery = useQuery<CustomerListType>({
    queryKey: ["customers", params],
    queryFn: async () => {
      const response = await apiClient.get("/customers", { params });
      return customerListSchema.parse(response.data);
    },
  });

  const createCustomerMutation = useMutation({
    mutationFn: async (payload: CustomerRequestType) => {
      const parsedPayload = customerRequestSchema.parse(payload);
      const response = await apiClient.post("/customers", parsedPayload);
      return customerSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });

  const updateCustomerMutation = useMutation({
    mutationFn: async (params: {
      customerId: string;
      payload: Partial<Omit<CustomerRequestType, "customer_type" | "identification_number">> & {
        is_active?: boolean;
      };
    }) => {
      const updateSchema = z.object({
        name: z.string().min(2).max(150).optional(),
        email: z.string().email().optional(),
        phone: z.string().max(20).optional(),
        address: z.string().max(300).optional(),
        is_active: z.boolean().optional(),
      });
      const parsedPayload = updateSchema.parse(params.payload);
      const response = await apiClient.patch(`/customers/${params.customerId}`, parsedPayload);
      return customerSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });

  return {
    customers: customersQuery.data?.items ?? [],
    total: customersQuery.data?.total ?? 0,
    isLoading: customersQuery.isLoading,
    createCustomer: createCustomerMutation.mutateAsync,
    updateCustomer: updateCustomerMutation.mutateAsync,
  };
}
