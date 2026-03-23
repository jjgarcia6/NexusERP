import { useEffect, useState } from "react";
import { AxiosError } from "axios";

import {
  apiClient,
  healthSchema,
  serviceUnavailableSchema,
} from "../../../shared";

type HealthStatus = "ok" | "error";

type UseHealthCheckResult = {
  status: HealthStatus;
  isLoading: boolean;
  isError: boolean;
};

export function useHealthCheck(): UseHealthCheckResult {
  const [status, setStatus] = useState<HealthStatus>("error");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchHealth = async (): Promise<void> => {
      try {
        const response = await apiClient.get("/health");
        const parsed = healthSchema.safeParse(response.data);
        if (!isMounted) {
          return;
        }
        setStatus(parsed.success ? "ok" : "error");
      } catch (error) {
        if (!isMounted) {
          return;
        }
        if (error instanceof AxiosError && error.response?.status === 503) {
          const degraded = serviceUnavailableSchema.safeParse(error.response.data);
          setStatus(degraded.success ? "error" : "error");
        } else {
          setStatus("error");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchHealth();

    return () => {
      isMounted = false;
    };
  }, []);

  return {
    status,
    isLoading,
    isError: status === "error" && !isLoading,
  };
}
