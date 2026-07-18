/** Página de horarios guardados.
 *
 * Muestra los horarios favoritos del usuario.
 */
import type { ReactElement } from "react";

import { AppShell } from "@/components/layout/AppShell";

function SavedPage(): ReactElement {
  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold text-clay-text">
        Mis Horarios Guardados
      </h1>

      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-clay-lg border-0 bg-white/70 p-8 shadow-clay backdrop-blur-md text-center">
        <p className="mb-2 text-lg font-semibold text-clay-text">
          Aún no has guardado ningún horario
        </p>
        <p className="text-clay-text-secondary">
          Genera combinaciones sin choques y guarda tus favoritos.
        </p>
      </div>
    </AppShell>
  );
}

export default SavedPage;
