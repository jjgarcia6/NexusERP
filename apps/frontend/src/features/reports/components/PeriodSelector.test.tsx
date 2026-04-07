import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { PeriodSelector } from "./PeriodSelector";

describe("PeriodSelector", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-04-10T12:00:00.000Z"));
  });

  afterEach(() => {
    cleanup();
    vi.useRealTimers();
  });

  it("should_calculate_correct_dates_for_last_7_days_preset", () => {
    const onChange = vi.fn();

    render(
      <PeriodSelector
        value={{ from: "2026-04-10T00:00:00.000Z", to: "2026-04-10T23:59:59.999Z" }}
        onChange={onChange}
      />,
    );

    fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "last7days" },
    });

    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith({
      from: "2026-04-03T00:00:00.000Z",
      to: "2026-04-10T12:00:00.000Z",
    });
  });

  it("should_show_validation_error_when_from_is_after_to", () => {
    render(
      <PeriodSelector
        value={{ from: "2026-04-10T00:00:00.000Z", to: "2026-04-10T23:59:59.999Z" }}
        onChange={vi.fn()}
      />,
    );

    fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "custom" },
    });

    const dateInputs = screen.getAllByDisplayValue("2026-04-10");
    fireEvent.change(dateInputs[0], { target: { value: "2026-04-12" } });
    fireEvent.change(dateInputs[1], { target: { value: "2026-04-10" } });
    fireEvent.click(screen.getByRole("button", { name: "Aplicar" }));

    expect(screen.getByText("La fecha de inicio DEBE ser anterior a la fecha de fin")).toBeInTheDocument();
  });

  it("should_not_call_onChange_when_dates_are_invalid", () => {
    const onChange = vi.fn();

    render(
      <PeriodSelector
        value={{ from: "2026-04-10T00:00:00.000Z", to: "2026-04-10T23:59:59.999Z" }}
        onChange={onChange}
      />,
    );

    fireEvent.change(screen.getByRole("combobox"), {
      target: { value: "custom" },
    });

    const dateInputs = screen.getAllByDisplayValue("2026-04-10");
    fireEvent.change(dateInputs[0], { target: { value: "2026-04-20" } });
    fireEvent.change(dateInputs[1], { target: { value: "2026-04-10" } });
    fireEvent.click(screen.getByRole("button", { name: "Aplicar" }));

    expect(onChange).not.toHaveBeenCalled();
  });
});
