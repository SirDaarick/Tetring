/** Página de perfil y configuración.
 *
 * Muestra información de la cuenta y opciones de sesión.
 */
import type { ReactElement } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, type SaesProfileResponse } from "@/lib/api";
import { SaesConnectionWizard } from "@/components/saes/SaesConnectionWizard";

export function ProfilePage(): ReactElement {
  const { user, logout } = useAuth();
  const queryClient = useQueryClient();
  const [wizardOpen, setWizardOpen] = useState(false);

  const { data: saesProfile, isLoading } = useQuery({
    queryKey: ["saes", "profile"],
    queryFn: () => api.get<SaesProfileResponse>("/saes/profile").then(res => res.data),
    retry: false
  });

  const unlinkMutation = useMutation({
    mutationFn: () => api.post("/saes/unlink"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saes", "profile"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("SAES desvinculado correctamente");
    },
    onError: () => toast.error("Error al desvincular SAES")
  });

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
          <h2 className="mb-4 text-lg font-semibold text-clay-text">Cuenta SAES</h2>
          {isLoading ? (
            <p className="text-sm text-clay-text-secondary">Cargando estado...</p>
          ) : saesProfile ? (
            <div className="space-y-4">
              <div className="space-y-1">
                <p className="text-sm text-clay-text-secondary">
                  Boleta: <span className="text-clay-text font-medium">{saesProfile.boleta}</span>
                </p>
                <p className="text-sm text-clay-text-secondary">
                  Escuela: <span className="text-clay-text font-medium">{saesProfile.escuela_nombre || saesProfile.escuela}</span>
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => unlinkMutation.mutate()}
                  disabled={unlinkMutation.isPending}
                  className="rounded-2xl border-clay-border bg-white/70 text-clay-text shadow-clay hover:bg-clay-surface"
                >
                  Desvincular SAES
                </Button>
                <Button 
                  onClick={() => setWizardOpen(true)}
                  className="rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary text-white shadow-clay hover:-translate-y-0.5 hover:shadow-clay-lg active:scale-[0.95]"
                >
                  Actualizar Sesión (SAES)
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-clay-text-secondary">No has vinculado tu cuenta SAES aún.</p>
              <Button 
                onClick={() => setWizardOpen(true)}
                className="rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary text-white shadow-clay hover:-translate-y-0.5"
              >
                Vincular SAES
              </Button>
            </div>
          )}
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

      <SaesConnectionWizard 
        open={wizardOpen} 
        onOpenChange={setWizardOpen} 
        onSuccess={() => {
          setWizardOpen(false);
          queryClient.invalidateQueries({ queryKey: ["saes", "profile"] });
          queryClient.invalidateQueries({ queryKey: ["dashboard"] });
          toast.success("SAES conectado correctamente");
        }} 
      />
    </AppShell>
  );
}

export default ProfilePage;
