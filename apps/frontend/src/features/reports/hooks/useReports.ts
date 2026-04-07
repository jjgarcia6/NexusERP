import { useQuery } from "@tanstack/react-query";

import apiClient from "../../../shared/api/client";
import {
  customerReportSchema,
  granularitySchema,
  inventoryReportSchema,
  purchasesReportSchema,
  salesReportSchema,
  type CustomerReportType,
  type GranularityType,
  type InventoryReportType,
  type PeriodRange,
  type PurchasesReportType,
  type SalesReportType,
} from "../types/reports.types";

type ReportType = "sales" | "inventory" | "customers" | "purchases";

type UseReportsParams = {
  type: ReportType;
  period: PeriodRange;
  granularity?: GranularityType;
};

type ReportsDataType =
  | SalesReportType
  | InventoryReportType
  | CustomerReportType
  | PurchasesReportType;

type UseReportsResult = {
  data: ReportsDataType | null;
  isLoading: boolean;
  isError: boolean;
};

export function useReports(params: UseReportsParams): UseReportsResult {
  const query = useQuery<ReportsDataType>({
    queryKey: ["reports", params.type, params.period, params.granularity],
    queryFn: async () => {
      const baseParams = {
        from: params.period.from,
        to: params.period.to,
      };

      switch (params.type) {
        case "sales": {
          const granularity = params.granularity
            ? granularitySchema.parse(params.granularity)
            : "day";
          const response = await apiClient.get("/reports/sales", {
            params: {
              ...baseParams,
              granularity,
            },
          });
          return salesReportSchema.parse(response.data);
        }
        case "inventory": {
          const response = await apiClient.get("/reports/inventory", {
            params: baseParams,
          });
          return inventoryReportSchema.parse(response.data);
        }
        case "customers": {
          const response = await apiClient.get("/reports/customers", {
            params: baseParams,
          });
          return customerReportSchema.parse(response.data);
        }
        case "purchases": {
          const response = await apiClient.get("/reports/purchases", {
            params: baseParams,
          });
          return purchasesReportSchema.parse(response.data);
        }
      }
    },
    staleTime: 60_000,
  });

  return {
    data: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}
