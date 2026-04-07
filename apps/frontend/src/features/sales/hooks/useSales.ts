import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "../../../shared/api/client";
import {
  saleListSchema,
  saleSchema,
  type SaleListType,
  type SaleRequestType,
  type SaleType,
} from "../types/sales.types";

type SalesParams = {
  status?: string;
  customer_id?: string;
  from?: string;
  to?: string;
  skip?: number;
  limit?: number;
  saleId?: string;
};

export function useSales(params: SalesParams = {}) {
  const queryClient = useQueryClient();
  const { saleId, ...listParams } = params;

  const listQuery = useQuery<SaleListType>({
    queryKey: ["sales", listParams],
    queryFn: async () => {
      const response = await apiClient.get("/sales", { params: listParams });
      return saleListSchema.parse(response.data);
    },
  });

  const detailQuery = useQuery<SaleType>({
    queryKey: ["sales", "detail", saleId],
    queryFn: async () => {
      const response = await apiClient.get(`/sales/${saleId}`);
      return saleSchema.parse(response.data);
    },
    enabled: Boolean(saleId),
  });

  const createSale = useMutation({
    mutationFn: async (sale: SaleRequestType) => {
      const response = await apiClient.post("/sales", sale);
      return saleSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["sales"] });
      await queryClient.invalidateQueries({ queryKey: ["stock"] });
    },
  });

  const confirmSale = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.patch(`/sales/${id}/confirm`);
      return saleSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["sales"] });
      await queryClient.invalidateQueries({ queryKey: ["stock"] });
    },
  });

  const cancelSale = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.patch(`/sales/${id}/cancel`);
      return saleSchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["sales"] });
      await queryClient.invalidateQueries({ queryKey: ["stock"] });
    },
  });

  return {
    sales: listQuery.data?.items ?? [],
    total: listQuery.data?.total ?? 0,
    sale: detailQuery.data ?? null,
    isLoading: listQuery.isLoading || detailQuery.isLoading,
    createSale: createSale.mutateAsync,
    confirmSale: confirmSale.mutateAsync,
    cancelSale: cancelSale.mutateAsync,
  };
}
