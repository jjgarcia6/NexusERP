import { useQuery } from "@tanstack/react-query";

import apiClient from "../../../shared/api/client";
import {
  dashboardSchema,
  type DashboardType,
  type PeriodRange,
} from "../types/reports.types";

type UseDashboardParams = {
  period: PeriodRange;
};

type UseDashboardResult = {
  dashboard: DashboardType | null;
  isLoading: boolean;
  isError: boolean;
};

export function useDashboard(params: UseDashboardParams): UseDashboardResult {
  const query = useQuery<DashboardType>({
    queryKey: ["dashboard", params.period],
    queryFn: async () => {
      const response = await apiClient.get("/reports", {
        params: {
          from: params.period.from,
          to: params.period.to,
        },
      });
      return dashboardSchema.parse(response.data);
    },
    staleTime: 60_000,
  });

  return {
    dashboard: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}
