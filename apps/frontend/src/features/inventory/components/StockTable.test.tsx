import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { StockTable } from "./StockTable";

const useAuthMock = vi.fn();
const useProductsMock = vi.fn();
const useStockLevelsMock = vi.fn();
const useStockMovementsMock = vi.fn();

vi.mock("../../auth", () => ({
  useAuth: () => useAuthMock(),
}));

vi.mock("../../catalog/hooks/useProducts", () => ({
  useProducts: (...args: unknown[]) => useProductsMock(...args),
}));

vi.mock("../hooks/useStockLevels", () => ({
  useStockLevels: (...args: unknown[]) => useStockLevelsMock(...args),
}));

vi.mock("../hooks/useStockMovements", () => ({
  useStockMovements: (...args: unknown[]) => useStockMovementsMock(...args),
}));

function renderStockTable() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <StockTable />
    </QueryClientProvider>,
  );
}

describe("StockTable", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    useAuthMock.mockReset();
    useProductsMock.mockReset();
    useStockLevelsMock.mockReset();
    useStockMovementsMock.mockReset();

    useAuthMock.mockReturnValue({ user: { role: "admin" } });

    useProductsMock.mockReturnValue({
      products: [
        {
          id: "prd-1",
          name: "Producto Bajo",
          min_stock: 5,
        },
        {
          id: "prd-2",
          name: "Producto OK",
          min_stock: 2,
        },
        {
          id: "prd-3",
          name: "Producto Sin Stock",
          min_stock: 4,
        },
      ],
      isLoading: false,
    });

    useStockLevelsMock.mockReturnValue({
      stockLevels: [
        {
          product_id: "prd-1",
          product_name: "Producto Bajo",
          available_quantity: 2,
          min_stock: 5,
          low_stock: true,
          updated_at: "2026-03-24T10:00:00.000Z",
        },
        {
          product_id: "prd-2",
          product_name: "Producto OK",
          available_quantity: 10,
          min_stock: 2,
          low_stock: false,
          updated_at: "2026-03-24T10:00:00.000Z",
        },
      ],
      isLoading: false,
      initializeStock: vi.fn().mockResolvedValue(undefined),
    });

    useStockMovementsMock.mockReturnValue({
      registerMovement: vi.fn().mockResolvedValue(undefined),
    });
  });

  it("should_show_low_stock_badge_when_available_quantity_below_min_stock", () => {
    renderStockTable();

    expect(screen.getByText("Stock bajo")).toBeInTheDocument();
  });

  it("should_show_ok_badge_when_available_quantity_above_min_stock", () => {
    renderStockTable();

    expect(screen.getAllByText("OK").length).toBeGreaterThan(0);
  });

  it("should_show_movement_button_for_admin_and_bodeguero", () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <StockTable />
      </QueryClientProvider>,
    );
    expect(screen.getAllByRole("button", { name: "Registrar movimiento" }).length).toBeGreaterThan(0);

    useAuthMock.mockReturnValue({ user: { role: "bodeguero" } });
    rerender(
      <QueryClientProvider client={queryClient}>
        <StockTable />
      </QueryClientProvider>,
    );
    expect(screen.getAllByRole("button", { name: "Registrar movimiento" }).length).toBeGreaterThan(0);
  });

  it("should_hide_movement_button_for_vendedor", () => {
    useAuthMock.mockReturnValue({ user: { role: "vendedor" } });

    renderStockTable();

    expect(screen.queryByRole("button", { name: "Registrar movimiento" })).not.toBeInTheDocument();
  });

  it("should_show_initialize_button_for_admin_when_stock_not_initialized", () => {
    renderStockTable();

    expect(screen.getByRole("button", { name: "Inicializar" })).toBeInTheDocument();
  });
});
