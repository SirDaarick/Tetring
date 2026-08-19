/** Formulario de inicio de sesión con email y contraseña.
 *
 * Aplica estilos claymorphism y maneja estados de carga y error.
 */
import type { ReactElement } from "react";
import { useState } from "react";
import { Eye, EyeOff, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";
import { extractErrorMessage } from "@/lib/api";

interface LoginFormProps {
  onSuccess?: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps): ReactElement {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth();

  async function handleSubmit(event: React.FormEvent): Promise<void> {
    event.preventDefault();
    setError(null);

    if (!email.trim()) {
      setError("Ingresa tu correo electrónico");
      return;
    }

    if (!password) {
      setError("Ingresa tu contraseña");
      return;
    }

    setIsLoading(true);
    try {
      await login(email, password);
      onSuccess?.();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="space-y-2">
        <Label htmlFor="login-email" className="text-clay-text">
          Correo electrónico
        </Label>
        <Input
          id="login-email"
          type="email"
          placeholder="alumno@ipn.mx"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isLoading}
          className="rounded-2xl border-0 bg-[#f4f1fa] py-6 shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="login-password" className="text-clay-text">
            Contraseña
          </Label>
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="text-sm text-clay-primary-soft transition-colors hover:text-clay-primary focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-1 rounded-sm"
            aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
          >
            {showPassword ? (
              <span className="flex items-center gap-1">
                <EyeOff className="h-4 w-4" /> Ocultar
              </span>
            ) : (
              <span className="flex items-center gap-1">
                <Eye className="h-4 w-4" /> Mostrar
              </span>
            )}
          </button>
        </div>
        <Input
          id="login-password"
          type={showPassword ? "text" : "password"}
          placeholder="••••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isLoading}
          className="rounded-2xl border-0 bg-[#f4f1fa] py-6 shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
        />
      </div>

      <div className="text-right">
        <button
          type="button"
          className="text-sm text-clay-text-secondary transition-colors hover:text-clay-primary focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-1 rounded-sm"
        >
          ¿Olvidaste tu contraseña?
        </button>
      </div>

      {error ? (
        <p className="text-sm text-clay-error" role="alert">
          {error}
        </p>
      ) : null}

      <Button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary py-6 text-base font-semibold text-white shadow-clay transition-all duration-300 hover:-translate-y-0.5 hover:shadow-clay-lg active:scale-[0.92] active:shadow-clay-pressed disabled:opacity-60 focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Ingresando...
          </>
        ) : (
          "Ingresar"
        )}
      </Button>
    </form>
  );
}
