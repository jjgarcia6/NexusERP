import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { PurchaseOrderType } from "../types/purchases.types";
import { PurchaseOrderDetail } from "./PurchaseOrderDetail";

function buildOrder(status: PurchaseOrderType["status"]): PurchaseOrderType {
  return {
    id: "order-12345678",
    supplier_id: "sup-1",
    supplier_name: "Proveedor Uno",
    status,
    lines: [
      {
        product_id: "prd-1",
        product_name: "Producto Uno",
        quantity: 2,
        unit_cost: 10,
        subtotal: 20,
      },
    ],
    total: 20,
    notes: "Nota interna",
    confirmed_at: status === "confirmed" || status === "received" ? "2026-03-24T12:00:00.000Z" : null,
    received_at: status === "received" ? "2026-03-24T13:00:00.000Z" : null,
    cancelled_at: null,
    created_at: "2026-03-24T11:00:00.000Z",
    updated_at: "2026-03-24T11:00:00.000Z",
  };
}

describe("PurchaseOrderDetail", () => {
  it("should_show_confirm_button_only_for_admin_in_draft_status", () => {
    const onConfirm = vi.fn().mockResolvedValue(undefined);
    const order = buildOrder("draft");

    const { rerender } = render(
      <PurchaseOrderDetail order={order} role="admin" onConfirm={onConfirm} />
    );

    expect(screen.getByRole("button", { name: "Confirmar" })).toBeInTheDocument();

    rerender(<PurchaseOrderDetail order={order} role="bodeguero" onConfirm={onConfirm} />);
    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
  });

  it("should_show_receive_button_for_admin_and_bodeguero_in_confirmed_status", () => {
    const onReceive = vi.fn().mockResolvedValue(undefined);
    const order = buildOrder("confirmed");

    const { rerender } = render(
      <PurchaseOrderDetail order={order} role="admin" onReceive={onReceive} />
    );
    expect(screen.getByRole("button", { name: "Recibir" })).toBeInTheDocument();

    rerender(<PurchaseOrderDetail order={order} role="bodeguero" onReceive={onReceive} />);
    expect(screen.getByRole("button", { name: "Recibir" })).toBeInTheDocument();
  });

  it("should_hide_all_action_buttons_for_received_order", () => {
    const order = buildOrder("received");

    render(
      <PurchaseOrderDetail
        order={order}
        role="admin"
        onConfirm={vi.fn().mockResolvedValue(undefined)}
        onReceive={vi.fn().mockResolvedValue(undefined)}
        onCancel={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(screen.queryByRole("button", { name: "Confirmar" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Recibir" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Cancelar" })).not.toBeInTheDocument();
  });

  it("should_show_error_notification_when_receive_returns_503", () => {
    const order = buildOrder("confirmed");

    render(
      <PurchaseOrderDetail
        order={order}
        role="bodeguero"
        onReceive={vi.fn().mockResolvedValue(undefined)}
        actionErrorMessage="No se pudo actualizar el inventario. Intente nuevamente"
      />
    );

    expect(
      screen.getByText("No se pudo actualizar el inventario. Intente nuevamente")
    ).toBeInTheDocument();
  });
});
