import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LoginForm } from "./LoginForm";

const loginMock = vi.fn();

const authState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  errorMessage: null as string | null,
  login: loginMock,
  logout: vi.fn(),
  register: vi.fn(),
};

vi.mock("../hooks/useAuth", () => ({
  useAuth: () => authState,
}));

describe("LoginForm", () => {
  it("should_show_validation_error_when_email_is_invalid", async () => {
    authState.isLoading = false;
    authState.errorMessage = null;

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText("Correo electrónico"), {
      target: { value: "correo" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "Password1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));

    expect(await screen.findByText("Correo electrónico inválido")).toBeInTheDocument();
  });

  it("should_show_validation_error_when_password_is_empty", async () => {
    authState.isLoading = false;
    authState.errorMessage = null;

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText("Correo electrónico"), {
      target: { value: "user@nexus.example.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));

    expect(await screen.findByText("La contraseña es requerida")).toBeInTheDocument();
  });

  it("should_call_login_when_form_is_valid", async () => {
    authState.isLoading = false;
    authState.errorMessage = null;
    loginMock.mockResolvedValueOnce(undefined);

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText("Correo electrónico"), {
      target: { value: "user@nexus.example.com" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "Password1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalled();
    });
  });

  it("should_show_server_error_when_login_fails", () => {
    authState.isLoading = false;
    authState.errorMessage = "Credenciales inválidas";

    render(<LoginForm />);

    expect(screen.getByText("Credenciales inválidas")).toBeInTheDocument();
  });

  it("should_disable_submit_button_while_loading", () => {
    authState.isLoading = true;
    authState.errorMessage = null;

    render(<LoginForm />);

    expect(screen.getByRole("button", { name: "Ingresando..." })).toBeDisabled();
  });
});
