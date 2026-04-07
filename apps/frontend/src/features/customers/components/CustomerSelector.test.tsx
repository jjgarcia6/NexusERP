import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { CustomerSelector } from "./CustomerSelector";

const useCustomerSearchMock = vi.fn();

vi.mock("../hooks/useCustomerSearch", () => ({
  useCustomerSearch: (query: string) => useCustomerSearchMock(query),
}));

describe("CustomerSelector", () => {
  beforeEach(() => {
    useCustomerSearchMock.mockReset();
    useCustomerSearchMock.mockReturnValue({
      results: [],
      isLoading: false,
    });
  });

  afterEach(() => {
    cleanup();
  });

  it("should_not_call_api_when_query_has_less_than_two_chars", () => {
    render(<CustomerSelector onSelect={vi.fn()} />);

    fireEvent.change(screen.getByPlaceholderText("Buscar cliente por nombre o identificacion"), {
      target: { value: "a" },
    });

    const lastCall = useCustomerSearchMock.mock.calls.at(-1);
    expect(lastCall?.[0]).toBe("a");
    expect(screen.queryByText("Sin resultados.")).not.toBeInTheDocument();
  });

  it("should_show_results_when_query_has_two_or_more_chars", () => {
    useCustomerSearchMock.mockImplementation((query: string) => {
      if (query.trim().length >= 2) {
        return {
          results: [
            {
              id: "cus-1",
              name: "Cliente Uno",
              identification_number: "1710034065",
              customer_type: "persona_natural",
            },
          ],
          isLoading: false,
        };
      }

      return { results: [], isLoading: false };
    });

    render(<CustomerSelector onSelect={vi.fn()} />);

    fireEvent.change(screen.getByPlaceholderText("Buscar cliente por nombre o identificacion"), {
      target: { value: "Cl" },
    });

    expect(screen.getByText("Cliente Uno - 1710034065")).toBeInTheDocument();
  });

  it("should_call_onSelect_callback_when_result_is_clicked", () => {
    const onSelect = vi.fn();
    useCustomerSearchMock.mockReturnValue({
      results: [
        {
          id: "cus-1",
          name: "Cliente Uno",
          identification_number: "1710034065",
          customer_type: "persona_natural",
        },
      ],
      isLoading: false,
    });

    render(<CustomerSelector onSelect={onSelect} />);

    fireEvent.change(screen.getByPlaceholderText("Buscar cliente por nombre o identificacion"), {
      target: { value: "Cl" },
    });

    fireEvent.click(screen.getByRole("button", { name: /Cliente Uno - 1710034065/i }));

    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect.mock.calls[0][0]).toEqual({
      id: "cus-1",
      name: "Cliente Uno",
      identification_number: "1710034065",
      customer_type: "persona_natural",
    });
  });

  it("should_show_selected_customer_name_in_input_after_selection", () => {
    useCustomerSearchMock.mockReturnValue({
      results: [
        {
          id: "cus-1",
          name: "Cliente Uno",
          identification_number: "1710034065",
          customer_type: "persona_natural",
        },
      ],
      isLoading: false,
    });

    render(<CustomerSelector onSelect={vi.fn()} />);

    const input = screen.getByPlaceholderText("Buscar cliente por nombre o identificacion") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "Cl" } });
    fireEvent.click(screen.getByRole("button", { name: /Cliente Uno - 1710034065/i }));

    expect(input.value).toBe("Cliente Uno - 1710034065");
  });
});
