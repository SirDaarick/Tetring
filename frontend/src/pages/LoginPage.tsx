/** Página de inicio de sesión y registro.
 *
 * Incluye toggle entre tabs, formularios y botón de Google.
 */
import type { ReactElement } from "react";
import { useNavigate } from "react-router-dom";

import { LoginForm } from "@/components/auth/LoginForm";
import { RegisterForm } from "@/components/auth/RegisterForm";
import { GoogleButton } from "@/components/auth/GoogleButton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Square } from "lucide-react";

export function LoginPage(): ReactElement {
  const navigate = useNavigate();

  function handleAuthSuccess(): void {
    navigate("/dashboard", { replace: true });
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f4f1fa] p-4">
      <div className="w-full max-w-md animate-scale-in">
        <div className="mb-8 text-center">
          <div className="mb-4 flex items-center justify-center gap-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-clay-primary-soft to-clay-primary text-white shadow-clay">
              <Square className="h-6 w-6" />
            </div>
            <span className="text-3xl font-bold text-clay-text">TETRING</span>
          </div>
          <p className="text-clay-text-secondary">Generador de Horarios IPN</p>
        </div>

        <div className="rounded-clay-xl border-0 bg-white/70 p-6 shadow-clay-lg backdrop-blur-md md:p-8">
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="mb-6 grid w-full grid-cols-2 rounded-2xl bg-clay-surface p-1">
              <TabsTrigger
                value="login"
                className="rounded-xl text-clay-text data-[state=active]:bg-white data-[state=active]:text-clay-primary data-[state=active]:shadow-clay"
              >
                Iniciar sesión
              </TabsTrigger>
              <TabsTrigger
                value="register"
                className="rounded-xl text-clay-text data-[state=active]:bg-white data-[state=active]:text-clay-primary data-[state=active]:shadow-clay"
              >
                Crear cuenta
              </TabsTrigger>
            </TabsList>

            <TabsContent value="login" className="mt-0">
              <LoginForm onSuccess={handleAuthSuccess} />
            </TabsContent>

            <TabsContent value="register" className="mt-0">
              <RegisterForm onSuccess={handleAuthSuccess} />
            </TabsContent>
          </Tabs>

          <div className="my-6 flex items-center gap-3">
            <Separator className="flex-1 bg-clay-border" />
            <span className="text-xs uppercase tracking-wider text-clay-text-secondary">
              o continúa con
            </span>
            <Separator className="flex-1 bg-clay-border" />
          </div>

          <GoogleButton />
        </div>

        <p className="mt-6 text-center text-sm text-clay-text-secondary">
          Términos de servicio · Privacidad
        </p>
      </div>
    </div>
  );
}
