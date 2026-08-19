/** Estado global de autenticación con Zustand.
 *
 * Persiste tokens en localStorage y gestiona el ciclo de vida de la sesión.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

import { api, type TokenResponse, type UserResponse } from "@/lib/api";

interface AuthState {
  user: UserResponse | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isSaesExpired: boolean;
  sidebarCollapsed: boolean;
}

interface AuthActions {
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: UserResponse | null) => void;
  setLoading: (isLoading: boolean) => void;
  setSaesExpired: (isSaesExpired: boolean) => void;
  toggleSidebar: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    full_name?: string;
  }) => Promise<void>;
  refreshSession: () => Promise<boolean>;
  logout: () => void;
  initializeAuth: () => Promise<void>;
}

const STORAGE_KEY = "auth-storage";

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,
      isSaesExpired: false,
      sidebarCollapsed: false,

      setTokens: (accessToken, refreshToken) => {
        set({
          accessToken,
          refreshToken,
          isAuthenticated: true,
        });
      },

      setUser: (user) => {
        set({ user });
      },

      setLoading: (isLoading) => {
        set({ isLoading });
      },

      setSaesExpired: (isSaesExpired) => {
        set({ isSaesExpired });
      },

      toggleSidebar: () => {
        set({ sidebarCollapsed: !get().sidebarCollapsed });
      },

      login: async (email, password) => {
        const { data } = await api.post<TokenResponse>("/auth/login", {
          email,
          password,
        });

        get().setTokens(data.access_token, data.refresh_token);
        const { data: user } = await api.get<UserResponse>("/auth/me");
        get().setUser(user);
      },

      register: async ({ email, password, full_name }) => {
        await api.post<UserResponse>("/auth/register", {
          email,
          password,
          full_name,
        });

        await get().login(email, password);
      },

      refreshSession: async () => {
        const refreshToken = get().refreshToken;
        if (!refreshToken) {
          return false;
        }

        try {
          const { data } = await api.post<TokenResponse>("/auth/refresh", {
            refresh_token: refreshToken,
          });

          get().setTokens(data.access_token, data.refresh_token);
          return true;
        } catch {
          get().logout();
          return false;
        }
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      initializeAuth: async () => {
        const { accessToken } = get();

        if (!accessToken) {
          set({ isAuthenticated: false, isLoading: false, user: null });
          return;
        }

        try {
          const { data: user } = await api.get<UserResponse>("/auth/me");
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          get().logout();
        } finally {
          set({ isLoading: false });
        }
      },
    }),
    {
      name: STORAGE_KEY,
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
