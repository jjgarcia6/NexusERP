import { create } from "zustand";

import type { UserType } from "../../features/auth/types/auth.types";

type AuthState = {
  accessToken: string | null;
  user: UserType | null;
  setTokenAndUser: (token: string, user: UserType) => void;
  setAccessToken: (token: string) => void;
  setUser: (user: UserType) => void;
  clearAuth: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setTokenAndUser: (token, user) => set({ accessToken: token, user }),
  setAccessToken: (token) => set({ accessToken: token }),
  setUser: (user) => set({ user }),
  clearAuth: () => set({ accessToken: null, user: null }),
}));
