import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProductList } from "./ProductList";

const navigateMock = vi.fn();
const useProductsMock = vi.fn();

const authState = {
  isAdmin: true,
};

const categoriesState = {
  categories: [
    {
      id: "cat-1",
      name: "Bebidas",
      description: "Liquidos",
      is_active: true,
      created_at: "2026-03-24T10:00:00.000Z",
      updated_at: "2026-03-24T10:00:00.000Z",
    },
  ],
  isLoading: false,
  createCategory: vi.fn(),
  updateCategory: vi.fn(),
  deleteCategory: vi.fn(),
};

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return {
    ...actual,
    useNavigate: () => navigateMock,
    useParams: () => ({}),
  };
});

vi.mock("../../auth", () => ({
  useAuth: () => authState,
}));

vi.mock("../hooks/useCategories", () => ({
  useCategories: () => categoriesState,
}));

vi.mock("../hooks/useProducts", () => ({
  useProducts: (...args: unknown[]) => useProductsMock(...args),
}));

vi.mock("@tanstack/react-query", async () => {
  const actual = await vi.importActual<typeof import("@tanstack/react-query")>("@tanstack/react-query");
  return {
    ...actual,
    useQuery: () => ({ isLoading: false, data: undefined }),
  };
});

describe("ProductList", () => {
  beforeEach(() => {
    useProductsMock.mockReset();
    useProductsMock.mockReturnValue({
      products: [
        {
          id: "prd-1",
          name: "Agua",
          description: "Botella",
          sku: "SKU-AGUA",
          price: 8.5,
          cost: 4.25,
          category_id: "cat-1",
          category_name: "Bebidas",
          image_url: "https://example.com/agua.jpg",
          is_active: true,
          created_at: "2026-03-24T10:00:00.000Z",
          updated_at: "2026-03-24T10:00:00.000Z",
        },
      ],
      total: 1,
      isLoading: false,
      createProduct: vi.fn().mockResolvedValue(undefined),
      updateProduct: vi.fn().mockResolvedValue(undefined),
    });

    authState.isAdmin = true;
  });

  it("should_render_product_list_when_data_is_loaded", () => {
    render(<ProductList />);

    expect(screen.getByRole("heading", { name: "Productos" })).toBeInTheDocument();
    expect(screen.getByText("Agua")).toBeInTheDocument();
    expect(screen.getByText("Mostrando 1 de 1 productos")).toBeInTheDocument();
  });

  it("should_filter_products_when_search_input_changes", async () => {
    vi.useFakeTimers();
    render(<ProductList />);

    fireEvent.change(screen.getByPlaceholderText("Buscar por nombre..."), {
      target: { value: "Ag" },
    });

    await act(async () => {
      vi.advanceTimersByTime(350);
    });

    const calls = useProductsMock.mock.calls;
    const lastParams = calls.at(-1)?.[0] as { search?: string } | undefined;
    expect(lastParams?.search).toBe("Ag");
    vi.useRealTimers();
  });

  it("should_show_create_button_only_for_admin", () => {
    const { rerender } = render(<ProductList />);
    expect(screen.getByRole("button", { name: "Nuevo producto" })).toBeInTheDocument();

    authState.isAdmin = false;
    rerender(<ProductList />);
    expect(screen.queryByRole("button", { name: "Nuevo producto" })).not.toBeInTheDocument();
  });

  it("should_hide_cost_column_for_vendedor", () => {
    authState.isAdmin = false;
    render(<ProductList />);

    expect(screen.queryByRole("columnheader", { name: "Costo" })).not.toBeInTheDocument();
  });

  it("should_show_empty_state_when_no_products_match", () => {
    useProductsMock.mockReturnValue({
      products: [],
      total: 0,
      isLoading: false,
      createProduct: vi.fn().mockResolvedValue(undefined),
      updateProduct: vi.fn().mockResolvedValue(undefined),
    });

    render(<ProductList />);

    expect(screen.getByText("Mostrando 0 de 0 productos")).toBeInTheDocument();
  });
});
