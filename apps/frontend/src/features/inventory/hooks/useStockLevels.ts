import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "../../../shared/api/client";
import {
  stockInitRequestSchema,
  stockLevelSchema,
  stockListSchema,
  type StockInitRequestType,
  type StockLevelType,
} from "../types/inventory.types";

type UseStockLevelsParams = {
  low_stock?: boolean;
  skip?: number;
  limit?: number;
};

type UseStockLevelsResult = {
  stockLevels: StockLevelType[];
  total: number;
  isLoading: boolean;
  initializeStock: (params: { productId: string; payload: StockInitRequestType }) => Promise<StockLevelType>;
};

export function useStockLevels(params: UseStockLevelsParams): UseStockLevelsResult {
  const queryClient = useQueryClient();

  const stockQuery = useQuery({
    queryKey: ["stock", params],
    queryFn: async () => {
      const response = await apiClient.get("/inventory/stock", { params });
      return stockListSchema.parse(response.data);
    },
  });

  const initializeMutation = useMutation({
    mutationFn: async (params: { productId: string; payload: StockInitRequestType }) => {
      const parsedPayload = stockInitRequestSchema.parse(params.payload);
      const response = await apiClient.post(
        `/inventory/stock/${params.productId}/initialize`,
        parsedPayload,
      );
      return stockLevelSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["stock"] });
    },
  });

  return {
    stockLevels: stockQuery.data?.items ?? [],
    total: stockQuery.data?.total ?? 0,
    isLoading: stockQuery.isLoading,
    initializeStock: initializeMutation.mutateAsync,
  };
}
