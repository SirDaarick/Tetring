/** Formulario de registro con indicador de fortaleza de contraseña.
 *
 * Valida longitud mínima y muestra feedback visual.
 */
import type { ReactElement } from "react";
import { useMemo, useState } from "react";
import { Eye, EyeOff, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { useAuth } from "@/hooks/useAuth";
import { extractErrorMessage } from "@/lib/api";

interface RegisterFormProps {
  onSuccess?: () => void;
}

function getPasswordStrength(password: string): { value: number; label: string; color: string } {
  if (password.length === 0) {
    return { value: 0, label: "", color: "bg-clay-border" };
  }

  let score = 0;
  if (password.length >= 8) score += 1;
  if (password.length >= 12) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/[0-9]/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  if (score <= 2) {
    return { value: 33, label: "Débil", color: "bg-clay-error" };
  }
  if (score <= 4) {
    return { value: 66, label: "Aceptable", color: "bg-clay-warning" };
  }
  return { value: 100, label: "Fuerte", color: "bg-clay-success" };
}

export function RegisterForm({ onSuccess }: RegisterFormProps): ReactElement {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { register } = useAuth();

  const strength = useMemo(() => getPasswordStrength(password), [password]);

  async function handleSubmit(event: React.FormEvent): Promise<void> {
    event.preventDefault();
    setError(null);

    if (!email.trim()) {
      setError("Ingresa tu correo electrónico");
      return;
    }

    if (password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres");
      return;
    }

    setIsLoading(true);
    try {
      await register({
        email,
        password,
        full_name: fullName.trim() || undefined,
      });
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
        <Label htmlFor="register-name" className="text-clay-text">
          Nombre completo (opcional)
        </Label>
        <Input
          id="register-name"
          type="text"
          placeholder="Juan Pérez García"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          disabled={isLoading}
          className="rounded-2xl border-0 bg-[#f4f1fa] py-6 shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="register-email" className="text-clay-text">
          Correo electrónico
        </Label>
        <Input
          id="register-email"
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
          <Label htmlFor="register-password" className="text-clay-text">
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
          id="register-password"
          type={showPassword ? "text" : "password"}
          placeholder="••••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isLoading}
          className="rounded-2xl border-0 bg-[#f4f1fa] py-6 shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
        />

        {password.length > 0 ? (
          <div className="space-y-1 pt-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-clay-text-secondary">Fortaleza</span>
              <span className="font-medium text-clay-text">{strength.label}</span>
            </div>
            <Progress value={strength.value} className="h-2 rounded-full bg-clay-surface">
              <div className={`h-full rounded-full ${strength.color} transition-all duration-300`} />
            </Progress>
          </div>
        ) : null}
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
            Creando cuenta...
          </>
        ) : (
          "Crear cuenta"
        )}
      </Button>
    </form>
  );
}
