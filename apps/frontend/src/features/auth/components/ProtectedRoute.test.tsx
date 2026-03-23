import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { useAuthStore } from "../../../shared/stores/auth.store";
import { ProtectedRoute } from "./ProtectedRoute";

function LoginProbe() {
  const location = useLocation();
  return <div>Login{location.search}</div>;
}

function renderWithRouter(initialEntry: string) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Route>
        <Route path="/login" element={<LoginProbe />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  it("should_redirect_to_login_when_user_is_not_authenticated", () => {
    useAuthStore.getState().clearAuth();

    renderWithRouter("/dashboard");

    expect(screen.getByText(/Login\?redirect=/)).toBeInTheDocument();
  });

  it("should_render_outlet_when_user_is_authenticated", () => {
    useAuthStore.getState().setAccessToken("token");

    renderWithRouter("/dashboard");

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("should_preserve_redirect_param_in_url_when_redirecting", () => {
    useAuthStore.getState().clearAuth();

    renderWithRouter("/dashboard");

    expect(screen.getByText("Login?redirect=%2Fdashboard")).toBeInTheDocument();
  });
});
