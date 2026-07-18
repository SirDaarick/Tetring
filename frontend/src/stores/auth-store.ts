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
}

interface AuthActions {
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: UserResponse | null) => void;
  setLoading: (isLoading: boolean) => void;
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
        const { accessToken, refreshToken } = get();

        if (!accessToken) {
          set({ isLoading: false });
          return;
        }

        try {
          const { data: user } = await api.get<UserResponse>("/auth/me");
          get().setUser(user);
        } catch {
          if (refreshToken) {
            const refreshed = await get().refreshSession();
            if (refreshed) {
              try {
                const { data: user } = await api.get<UserResponse>("/auth/me");
                get().setUser(user);
              } catch {
                get().logout();
              }
            }
          } else {
            get().logout();
          }
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
      }),
    }
  )
);
