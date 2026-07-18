/** Página de callback para autenticación con Google.
 *
 * Lee los tokens de la URL, los guarda y redirige al dashboard.
 */
import type { ReactElement } from "react";
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { Loader2 } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { api, type UserResponse } from "@/lib/api";

export function GoogleCallbackPage(): ReactElement {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");

    if (!accessToken || !refreshToken) {
      setError("No se recibieron los tokens de autenticación");
      return;
    }

    setTokens(accessToken, refreshToken);

    api
      .get<UserResponse>("/auth/me")
      .then(({ data }) => {
        setUser(data);
        navigate("/dashboard", { replace: true });
      })
      .catch(() => {
        setError("No se pudo obtener la información del usuario");
      });
  }, [searchParams, navigate, setTokens, setUser]);

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-[#f4f1fa] p-4 text-center">
        <h1 className="mb-2 text-xl font-bold text-clay-text">
          Error de autenticación
        </h1>
        <p className="mb-6 text-clay-text-secondary">{error}</p>
        <button
          onClick={() => navigate("/login", { replace: true })}
          className="rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary px-6 py-3 font-semibold text-white shadow-clay transition-all hover:-translate-y-0.5 hover:shadow-clay-lg active:scale-[0.92]"
        >
          Volver al inicio de sesión
        </button>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#f4f1fa]">
      <Loader2 className="mb-4 h-10 w-10 animate-spin text-clay-primary" />
      <p className="text-clay-text-secondary">Iniciando sesión...</p>
    </div>
  );
}
