import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import apiClient from "../../../shared/api/client";
import { useAuthStore } from "../../../shared/stores/auth.store";
import { loginSchema, tokenResponseSchema, userSchema } from "../types/auth.types";
import type { LoginType, RegisterType, UserType } from "../types/auth.types";

type UseAuthResult = {
  user: UserType | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isLoading: boolean;
  errorMessage: string | null;
  login: (data: LoginType) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: RegisterType) => Promise<void>;
};

export function useAuth(): UseAuthResult {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, accessToken, setTokenAndUser, setAccessToken, setUser, clearAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const isPublicAuthRoute = location.pathname === "/login" || location.pathname === "/register";
  const redirectAfterLogin = (() => {
    const redirectParam = new URLSearchParams(location.search).get("redirect");
    if (redirectParam && redirectParam.startsWith("/")) {
      return redirectParam;
    }
    return "/dashboard";
  })();

  const bootstrapSession = useCallback(async () => {
    try {
      const refreshResponse = await apiClient.post("/auth/refresh");
      const parsedToken = tokenResponseSchema.safeParse(refreshResponse.data);
      if (!parsedToken.success) {
        clearAuth();
        return;
      }

      setAccessToken(parsedToken.data.access_token);
      const meResponse = await apiClient.get("/auth/me");
      const parsedUser = userSchema.safeParse(meResponse.data);
      if (!parsedUser.success) {
        clearAuth();
        return;
      }

      setUser(parsedUser.data);
    } catch {
      clearAuth();
    }
  }, [clearAuth, setAccessToken, setUser]);

  useEffect(() => {
    if (!accessToken && !user && !isPublicAuthRoute) {
      void bootstrapSession();
    }
  }, [accessToken, bootstrapSession, isPublicAuthRoute, user]);

  const login = useCallback(
    async (data: LoginType) => {
      setErrorMessage(null);
      setIsLoading(true);

      try {
        const parsedPayload = loginSchema.parse(data);
        const tokenResponse = await apiClient.post("/auth/login", parsedPayload);
        const parsedToken = tokenResponseSchema.parse(tokenResponse.data);
        const meResponse = await apiClient.get("/auth/me", {
          headers: {
            Authorization: `Bearer ${parsedToken.access_token}`,
          },
        });
        const parsedUser = userSchema.parse(meResponse.data);
        setTokenAndUser(parsedToken.access_token, parsedUser);
        navigate(redirectAfterLogin, { replace: true });
      } catch (error) {
        setErrorMessage("Credenciales inválidas");
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [navigate, redirectAfterLogin, setTokenAndUser]
  );

  const logout = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      await apiClient.post("/auth/logout");
      clearAuth();
      navigate("/login", { replace: true });
    } finally {
      setIsLoading(false);
    }
  }, [clearAuth, navigate]);

  const register = useCallback(async (data: RegisterType) => {
    if (!accessToken || !user || user.role !== "admin") {
      setErrorMessage("Solo un administrador autenticado puede crear usuarios.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const payload = {
        email: data.email,
        password: data.password,
        full_name: data.full_name,
      };
      await apiClient.post("/auth/register", payload);
      navigate("/login", { replace: true });
    } catch {
      setErrorMessage("No se pudo crear la cuenta");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, navigate, user]);

  return useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(accessToken),
      isAdmin: user?.role === "admin",
      isLoading,
      errorMessage,
      login,
      logout,
      register,
    }),
    [user, accessToken, isLoading, errorMessage, login, logout, register]
  );
}
