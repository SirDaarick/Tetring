/** Envoltorio principal del layout autenticado.
 *
 * Incluye la sidebar, el área de contenido scrollable y el banner de sesión expirada.
 */
import type { ReactElement, ReactNode } from "react";
import { useState } from "react";

import { Sidebar } from "@/components/layout/Sidebar";
import { useAuthStore } from "@/stores/auth-store";
import { SaesConnectionWizard } from "@/components/saes/SaesConnectionWizard";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps): ReactElement {
  const isSaesExpired = useAuthStore((state) => state.isSaesExpired);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [bannerDismissed, setBannerDismissed] = useState(false);

  return (
    <div className="min-h-screen bg-[#f4f1fa] flex flex-col">
      {isSaesExpired && !bannerDismissed && (
        <div className="w-full bg-gradient-to-r from-amber-500/95 to-orange-500/95 text-white py-2.5 px-6 shadow-md backdrop-blur-md flex flex-wrap items-center justify-between gap-4 sticky top-0 z-50 transition-all duration-300">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 shrink-0 text-amber-100 animate-pulse" />
            <p className="text-sm font-medium">
              Tu sesión de SAES ha expirado. Si necesitas sincronizar kárdex o consultar cupos en vivo, actualiza tu sesión.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              onClick={() => setWizardOpen(true)}
              className="rounded-xl bg-white text-orange-600 hover:bg-orange-50 font-bold shadow-clay px-4 shrink-0 transition-transform active:scale-95 border-0"
            >
              Actualizar Sesión
            </Button>
            <button
              type="button"
              onClick={() => setBannerDismissed(true)}
              className="p-1 rounded-lg hover:bg-white/20 text-white/80 hover:text-white transition-colors"
              title="Descartar aviso"
            >
              ✕
            </button>
          </div>
        </div>
      )}
      
      <div className="flex-1 flex relative">
        <Sidebar />
        <main className="flex-1 min-h-screen bg-[#f4f1fa] pt-16 md:pt-0 min-w-0">
          <div className="p-6 lg:p-8">
            <div className="w-full">
              {children}
            </div>
          </div>
        </main>
      </div>

      <SaesConnectionWizard open={wizardOpen} onOpenChange={setWizardOpen} />
    </div>
  );
}
