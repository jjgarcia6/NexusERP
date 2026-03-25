import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { OrderStatusBadge } from "./OrderStatusBadge";

describe("OrderStatusBadge", () => {
  it("should_render_correct_badge_for_each_status", () => {
    const { rerender } = render(<OrderStatusBadge status="draft" />);
    expect(screen.getByText("Borrador")).toBeInTheDocument();

    rerender(<OrderStatusBadge status="confirmed" />);
    expect(screen.getByText("Confirmada")).toBeInTheDocument();

    rerender(<OrderStatusBadge status="received" />);
    expect(screen.getByText("Recibida")).toBeInTheDocument();

    rerender(<OrderStatusBadge status="cancelled" />);
    expect(screen.getByText("Cancelada")).toBeInTheDocument();
  });

  it("should_apply_correct_dark_mode_classes", () => {
    const { rerender } = render(<OrderStatusBadge status="draft" />);
    expect(screen.getByText("Borrador")).toHaveClass("dark:bg-gray-800", "dark:text-gray-300");

    rerender(<OrderStatusBadge status="confirmed" />);
    expect(screen.getByText("Confirmada")).toHaveClass("dark:bg-blue-900", "dark:text-blue-300");

    rerender(<OrderStatusBadge status="received" />);
    expect(screen.getByText("Recibida")).toHaveClass("dark:bg-green-900", "dark:text-green-300");

    rerender(<OrderStatusBadge status="cancelled" />);
    expect(screen.getByText("Cancelada")).toHaveClass("dark:bg-red-900", "dark:text-red-300");
  });
});
