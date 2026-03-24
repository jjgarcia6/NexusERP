import axios from "axios";

import { useAuthStore } from "../stores/auth.store";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 10_000,
  withCredentials: true,
});

let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as {
      _retry?: boolean;
      headers: Record<string, string>;
      [key: string]: unknown;
    };
    const requestUrl = String(originalRequest.url);
    const isAuthRequestWithoutRefresh =
      requestUrl.includes("/auth/login") ||
      requestUrl.includes("/auth/register") ||
      requestUrl.includes("/auth/logout");

    if (
      error.response?.status !== 401 ||
      originalRequest._retry ||
      requestUrl.includes("/auth/refresh") ||
      isAuthRequestWithoutRefresh
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (!isRefreshing) {
      isRefreshing = true;
      refreshPromise = apiClient
        .post("/auth/refresh")
        .then((response) => {
          const token = response.data?.access_token as string | undefined;
          if (!token) {
            throw new Error("Refresh response without access_token");
          }
          useAuthStore.getState().setAccessToken(token);
          return token;
        })
        .catch(() => {
          useAuthStore.getState().clearAuth();
          window.location.href = "/login";
          return null;
        })
        .finally(() => {
          isRefreshing = false;
        });
    }

    const refreshedToken = await refreshPromise;
    if (!refreshedToken) {
      return Promise.reject(error);
    }

    originalRequest.headers.Authorization = `Bearer ${refreshedToken}`;
    return apiClient(originalRequest);
  }
);

export default apiClient;
