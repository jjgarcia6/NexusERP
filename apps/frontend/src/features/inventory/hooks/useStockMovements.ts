import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "../../../shared/api/client";
import {
  stockMovementListSchema,
  stockMovementRequestSchema,
  stockMovementSchema,
  type StockMovementRequestType,
  type StockMovementType,
} from "../types/inventory.types";

type UseStockMovementsParams = {
  product_id?: string;
  type?: string;
  from?: string;
  to?: string;
  skip?: number;
  limit?: number;
};

type UseStockMovementsResult = {
  movements: StockMovementType[];
  total: number;
  isLoading: boolean;
  registerMovement: (payload: StockMovementRequestType) => Promise<StockMovementType>;
};

export function useStockMovements(params: UseStockMovementsParams): UseStockMovementsResult {
  const queryClient = useQueryClient();

  const movementsQuery = useQuery({
    queryKey: ["movements", params],
    queryFn: async () => {
      const response = await apiClient.get("/inventory/movements", { params });
      return stockMovementListSchema.parse(response.data);
    },
  });

  const registerMovementMutation = useMutation({
    mutationFn: async (payload: StockMovementRequestType) => {
      const parsedPayload = stockMovementRequestSchema.parse(payload);
      const response = await apiClient.post("/inventory/movements", parsedPayload);
      return stockMovementSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["movements"] });
      await queryClient.invalidateQueries({ queryKey: ["stock"] });
    },
  });

  return {
    movements: movementsQuery.data?.items ?? [],
    total: movementsQuery.data?.total ?? 0,
    isLoading: movementsQuery.isLoading,
    registerMovement: registerMovementMutation.mutateAsync,
  };
}
