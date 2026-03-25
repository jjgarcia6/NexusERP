import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import apiClient from "../../../shared/api/client";
import {
  categoryRequestSchema,
  categorySchema,
  type CategoryRequestType,
  type CategoryType,
} from "../types/catalog.types";

type UseCategoriesResult = {
  categories: CategoryType[];
  isLoading: boolean;
  createCategory: (payload: CategoryRequestType) => Promise<CategoryType>;
  updateCategory: (params: {
    categoryId: string;
    payload: Partial<CategoryRequestType>;
  }) => Promise<CategoryType>;
  deleteCategory: (categoryId: string) => Promise<void>;
};

export function useCategories(): UseCategoriesResult {
  const queryClient = useQueryClient();

  const categoriesQuery = useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const response = await apiClient.get("/categories");
      return categorySchema.array().parse(response.data);
    },
  });

  const createCategoryMutation = useMutation({
    mutationFn: async (payload: CategoryRequestType) => {
      const parsedPayload = categoryRequestSchema.parse(payload);
      const response = await apiClient.post("/categories", parsedPayload);
      return categorySchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });

  const updateCategoryMutation = useMutation({
    mutationFn: async (params: {
      categoryId: string;
      payload: Partial<CategoryRequestType>;
    }) => {
      const parsedPayload = categoryRequestSchema.partial().parse(params.payload);
      const response = await apiClient.patch(`/categories/${params.categoryId}`, parsedPayload);
      return categorySchema.parse(response.data);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });

  const deleteCategoryMutation = useMutation({
    mutationFn: async (categoryId: string) => {
      await apiClient.delete(`/categories/${categoryId}`);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });

  return {
    categories: categoriesQuery.data ?? [],
    isLoading: categoriesQuery.isLoading,
    createCategory: createCategoryMutation.mutateAsync,
    updateCategory: updateCategoryMutation.mutateAsync,
    deleteCategory: deleteCategoryMutation.mutateAsync,
  };
}
