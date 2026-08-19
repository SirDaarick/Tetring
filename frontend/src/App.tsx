/** Raíz de la aplicación: router, providers e inicialización de auth.
 *
 * Dashboard carga eager; el resto de páginas se cargan con lazy para reducir
 * el bundle inicial.
 */
import type { ReactElement } from "react";
import { useEffect, useState } from "react";
import { Suspense, lazy } from "react";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";

import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { DashboardPage } from "@/pages/DashboardPage";
import { LoginPage } from "@/pages/LoginPage";
import { GoogleCallbackPage } from "@/pages/GoogleCallbackPage";
import { useAuthStore } from "@/stores/auth-store";
import { queryClient } from "@/lib/query-client";
import { Skeleton } from "@/components/ui/skeleton";

const SchedulerPage = lazy(() => import("@/pages/SchedulerPage"));
const SavedPage = lazy(() => import("@/pages/SavedPage"));
const ProfilePage = lazy(() => import("@/pages/ProfilePage"));

function PageSkeleton(): ReactElement {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-[#f4f1fa]">
      <Skeleton className="h-12 w-48 rounded-clay" />
    </div>
  );
}

function AuthInitializer({ children }: { children: React.ReactNode }): ReactElement {
  const [ready, setReady] = useState(false);
  const initializeAuth = useAuthStore((state) => state.initializeAuth);

  useEffect(() => {
    initializeAuth()
      .catch(() => {})
      .finally(() => setReady(true));
  }, [initializeAuth]);

  if (!ready) {
    return <PageSkeleton />;
  }

  return <>{children}</>;
}

function ScrollToTop(): null {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

function AppRoutes(): ReactElement {
  return (
    <>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-clay-primary focus:px-4 focus:py-2 focus:text-white"
      >
        Saltar al contenido principal
      </a>
      <ScrollToTop />
      <main id="main-content">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<GoogleCallbackPage />} />
          <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/scheduler"
            element={
              <ProtectedRoute>
                <Suspense fallback={<PageSkeleton />}>
                  <SchedulerPage />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/saved"
            element={
              <ProtectedRoute>
                <Suspense fallback={<PageSkeleton />}>
                  <SavedPage />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Suspense fallback={<PageSkeleton />}>
                  <ProfilePage />
                </Suspense>
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </main>
    </>
  );
}

export function App(): ReactElement {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthInitializer>
          <AppRoutes />
        </AuthInitializer>
      </BrowserRouter>
      <Toaster
        position="bottom-right"
        toastOptions={{
          className:
            "rounded-clay border-0 bg-white/90 text-clay-text shadow-clay-lg backdrop-blur-md",
        }}
      />
    </QueryClientProvider>
  );
}

export default App;
