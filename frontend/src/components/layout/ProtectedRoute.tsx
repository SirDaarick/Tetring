/** Componente envoltorio para rutas protegidas.
 *
 * Redirige al login si el usuario no está autenticado.
 */
import type { ReactElement, ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useRequireAuth } from "@/hooks/useAuth";
import { Skeleton } from "@/components/ui/skeleton";

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({
  children,
}: ProtectedRouteProps): ReactElement | null {
  const { isAuthenticated, isLoading } = useRequireAuth();

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-[#f4f1fa]">
        <Skeleton className="h-12 w-48 rounded-clay" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
