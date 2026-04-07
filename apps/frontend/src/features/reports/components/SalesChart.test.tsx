import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { SalesChart } from "./SalesChart";

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  BarChart: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  CartesianGrid: () => null,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
  Bar: () => null,
}));

describe("SalesChart", () => {
  it("should_render_chart_with_correct_data", () => {
    render(
      <SalesChart
        entries={[
          {
            date: "2026-04-07",
            transactions: 2,
            subtotal_before_tax: "80.00",
            tax_amount: "9.60",
            total: "89.60",
          },
        ]}
      />,
    );

    expect(screen.getByText("Ventas por período")).toBeInTheDocument();
    expect(screen.getByTestId("responsive-container")).toBeInTheDocument();
  });

  it("should_show_empty_state_when_no_entries", () => {
    render(<SalesChart entries={[]} />);

    expect(screen.getByText("Sin datos para el período")).toBeInTheDocument();
  });
});
