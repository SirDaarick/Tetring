/** Hook de conveniencia para acceder al estado de autenticación.
 *
 * Re-exporta selectores y acciones del store de Zustand.
 */
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { useAuthStore } from "@/stores/auth-store";

export function useAuth() {
  return {
    user: useAuthStore((state) => state.user),
    accessToken: useAuthStore((state) => state.accessToken),
    refreshToken: useAuthStore((state) => state.refreshToken),
    isAuthenticated: useAuthStore((state) => state.isAuthenticated),
    isLoading: useAuthStore((state) => state.isLoading),
    login: useAuthStore((state) => state.login),
    register: useAuthStore((state) => state.register),
    refreshSession: useAuthStore((state) => state.refreshSession),
    logout: useAuthStore((state) => state.logout),
    setUser: useAuthStore((state) => state.setUser),
    setTokens: useAuthStore((state) => state.setTokens),
  };
}

export function useRequireAuth(): { isAuthenticated: boolean; isLoading: boolean } {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  return { isAuthenticated, isLoading };
}
