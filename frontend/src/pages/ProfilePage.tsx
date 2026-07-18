/** Página de perfil y configuración.
 *
 * Muestra información de la cuenta y opciones de sesión.
 */
import type { ReactElement } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

function ProfilePage(): ReactElement {
  const { user, logout } = useAuth();

  return (
    <AppShell>
      <h1 className="mb-6 text-2xl font-bold text-clay-text">Configuración</h1>

      <div className="mx-auto max-w-2xl space-y-6">
        <Card className="rounded-clay-lg border-0 bg-white/70 p-6 shadow-clay backdrop-blur-md">
          <h2 className="mb-4 text-lg font-semibold text-clay-text">
            Información personal
          </h2>
          <div className="space-y-3">
            <p className="text-clay-text-secondary">
              Correo: <span className="text-clay-text">{user?.email ?? "--"}</span>
            </p>
            <p className="text-clay-text-secondary">
              Nombre: <span className="text-clay-text">{user?.full_name ?? "--"}</span>
            </p>
          </div>
        </Card>

        <Card className="rounded-clay-lg border-0 bg-white/70 p-6 shadow-clay backdrop-blur-md">
          <h2 className="mb-4 text-lg font-semibold text-clay-text">Sesión</h2>
          <Button
            onClick={logout}
            className="rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary px-6 py-5 font-semibold text-white shadow-clay transition-all hover:-translate-y-0.5 hover:shadow-clay-lg active:scale-[0.92]"
          >
            Cerrar sesión
          </Button>
        </Card>
      </div>
    </AppShell>
  );
}

export default ProfilePage;
