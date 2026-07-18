/** Envoltorio principal del layout autenticado.
 *
 * Incluye la sidebar y el área de contenido scrollable.
 */
import type { ReactElement, ReactNode } from "react";

import { Sidebar } from "@/components/layout/Sidebar";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps): ReactElement {
  return (
    <div className="min-h-screen bg-[#f4f1fa]">
      <Sidebar />
      <main className="md:pl-20 lg:pl-60">
        <div className="p-6 lg:p-8">
          <div className="mx-auto max-w-7xl animate-float-in">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
