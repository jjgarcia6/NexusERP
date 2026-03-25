import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";

import apiClient from "../../../shared/api/client";
import {
  productListSchema,
  productRequestSchema,
  productSchema,
  type ProductListType,
  type ProductRequestType,
  type ProductType,
} from "../types/catalog.types";

type UseProductsParams = {
  search?: string;
  category_id?: string;
  skip?: number;
  limit?: number;
};

type UseProductsResult = {
  products: ProductType[];
  total: number;
  isLoading: boolean;
  createProduct: (payload: ProductRequestType) => Promise<ProductType>;
  updateProduct: (params: {
    productId: string;
    payload: Partial<ProductRequestType> & { is_active?: boolean };
  }) => Promise<ProductType>;
};

export function useProducts(params: UseProductsParams): UseProductsResult {
  const queryClient = useQueryClient();

  const productsQuery = useQuery<ProductListType>({
    queryKey: ["products", params],
    queryFn: async () => {
      const response = await apiClient.get("/products", { params });
      return productListSchema.parse(response.data);
    },
  });

  const createProductMutation = useMutation({
    mutationFn: async (payload: ProductRequestType) => {
      const parsedPayload = productRequestSchema.parse(payload);
      const response = await apiClient.post("/products", parsedPayload);
      return productSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });

  const updateProductMutation = useMutation({
    mutationFn: async (update: {
      productId: string;
      payload: Partial<ProductRequestType> & { is_active?: boolean };
    }) => {
      const updateSchema = z.object({
        name: z.string().min(2).max(200).optional(),
        sku: z.string().max(50).optional(),
        description: z.string().max(1000).optional(),
        category_id: z.string().optional(),
        cost: z.coerce.number().positive().optional(),
        price: z.coerce.number().positive().optional(),
        stock: z.number().int().nonnegative().optional(),
        is_active: z.boolean().optional(),
      });
      const parsedPayload = updateSchema.parse(update.payload);
      const response = await apiClient.patch(`/products/${update.productId}`, parsedPayload);
      return productSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["products"] });
    },
  });

  return {
    products: productsQuery.data?.items ?? [],
    total: productsQuery.data?.total ?? 0,
    isLoading: productsQuery.isLoading,
    createProduct: createProductMutation.mutateAsync,
    updateProduct: updateProductMutation.mutateAsync,
  };
}
