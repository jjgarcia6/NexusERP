import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { z } from "zod";

import apiClient from "../../../shared/api/client";
import {
  customerSearchResultSchema,
  type CustomerSearchResultType,
} from "../types/customers.types";

type UseCustomerSearchResult = {
  results: CustomerSearchResultType[];
  isLoading: boolean;
};

export function useCustomerSearch(query: string): UseCustomerSearchResult {
  const [debouncedQuery, setDebouncedQuery] = useState(query.trim());

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setDebouncedQuery(query.trim());
    }, 300);

    return () => {
      window.clearTimeout(timeout);
    };
  }, [query]);

  const searchQuery = useQuery({
    queryKey: ["customers", "search", debouncedQuery],
    queryFn: async () => {
      const response = await apiClient.get("/customers/search", {
        params: { q: debouncedQuery },
      });
      return z.array(customerSearchResultSchema).parse(response.data);
    },
    enabled: debouncedQuery.length >= 2,
    staleTime: 30_000,
  });

  return {
    results: searchQuery.data ?? [],
    isLoading: searchQuery.isLoading,
  };
}
