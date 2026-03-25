import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { isAxiosError } from "axios";

import apiClient from "../../../shared/api/client";
import {
  purchaseOrderListSchema,
  purchaseOrderRequestSchema,
  purchaseOrderSchema,
  type OrderStatusType,
  type PurchaseOrderRequestType,
  type PurchaseOrderType,
} from "../types/purchases.types";

type UsePurchaseOrdersParams = {
  orderId?: string;
  status?: OrderStatusType;
  supplier_id?: string;
  skip?: number;
  limit?: number;
};

type ReceiveOrderResult = {
  ok: boolean;
  order?: PurchaseOrderType;
  message?: string;
};

type UsePurchaseOrdersResult = {
  orders: PurchaseOrderType[];
  order: PurchaseOrderType | null;
  total: number;
  isLoading: boolean;
  isOrderLoading: boolean;
  errorMessage: string | null;
  createOrder: (payload: PurchaseOrderRequestType) => Promise<PurchaseOrderType>;
  confirmOrder: (orderId: string) => Promise<PurchaseOrderType>;
  receiveOrder: (orderId: string) => Promise<ReceiveOrderResult>;
  cancelOrder: (orderId: string) => Promise<PurchaseOrderType>;
};

export function usePurchaseOrders(params: UsePurchaseOrdersParams): UsePurchaseOrdersResult {
  const queryClient = useQueryClient();

  const ordersQuery = useQuery({
    queryKey: ["purchases", params],
    queryFn: async () => {
      const response = await apiClient.get("/purchases", { params });
      return purchaseOrderListSchema.parse(response.data);
    },
  });

  const orderQuery = useQuery({
    queryKey: ["purchases", params.orderId],
    enabled: Boolean(params.orderId),
    queryFn: async () => {
      const response = await apiClient.get(`/purchases/${params.orderId}`);
      return purchaseOrderSchema.parse(response.data);
    },
  });

  const createOrderMutation = useMutation({
    mutationFn: async (payload: PurchaseOrderRequestType) => {
      const parsedPayload = purchaseOrderRequestSchema.parse(payload);
      const response = await apiClient.post("/purchases", parsedPayload);
      return purchaseOrderSchema.parse(response.data);
    },
    onSuccess: async (order) => {
      await queryClient.invalidateQueries({ queryKey: ["purchases"] });
      await queryClient.invalidateQueries({ queryKey: ["purchases", order.id] });
    },
  });

  const confirmOrderMutation = useMutation({
    mutationFn: async (orderId: string) => {
      const response = await apiClient.patch(`/purchases/${orderId}/confirm`);
      return purchaseOrderSchema.parse(response.data);
    },
    onSuccess: async (order) => {
      await queryClient.invalidateQueries({ queryKey: ["purchases"] });
      await queryClient.invalidateQueries({ queryKey: ["purchases", order.id] });
    },
  });

  const receiveOrderMutation = useMutation({
    mutationFn: async (orderId: string): Promise<ReceiveOrderResult> => {
      try {
        const response = await apiClient.patch(`/purchases/${orderId}/receive`);
        const order = purchaseOrderSchema.parse(response.data);
        return { ok: true, order };
      } catch (error) {
        if (isAxiosError(error) && error.response?.status === 503) {
          const detail = error.response.data?.detail;
          const message = typeof detail === "string" ? detail : "No se pudo actualizar el inventario. Intente nuevamente";
          return { ok: false, message };
        }
        throw error;
      }
    },
    onSuccess: async (result) => {
      if (!result.ok || !result.order) {
        return;
      }
      await queryClient.invalidateQueries({ queryKey: ["purchases"] });
      await queryClient.invalidateQueries({ queryKey: ["purchases", result.order.id] });
    },
  });

  const cancelOrderMutation = useMutation({
    mutationFn: async (orderId: string) => {
      const response = await apiClient.patch(`/purchases/${orderId}/cancel`);
      return purchaseOrderSchema.parse(response.data);
    },
    onSuccess: async (order) => {
      await queryClient.invalidateQueries({ queryKey: ["purchases"] });
      await queryClient.invalidateQueries({ queryKey: ["purchases", order.id] });
    },
  });

  return {
    orders: ordersQuery.data?.items ?? [],
    order: orderQuery.data ?? null,
    total: ordersQuery.data?.total ?? 0,
    isLoading: ordersQuery.isLoading,
    isOrderLoading: orderQuery.isLoading,
    errorMessage: ordersQuery.isError ? "No fue posible cargar las órdenes." : null,
    createOrder: createOrderMutation.mutateAsync,
    confirmOrder: confirmOrderMutation.mutateAsync,
    receiveOrder: receiveOrderMutation.mutateAsync,
    cancelOrder: cancelOrderMutation.mutateAsync,
  };
}
