import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api, extractErrorMessage } from "@/lib/api";

interface School {
  id: string;
  name: string;
  url: string;
}

interface SaesConnectionWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function SaesConnectionWizard({
  open,
  onOpenChange,
  onSuccess,
}: SaesConnectionWizardProps) {
  const [step, setStep] = useState<"credentials" | "captcha" | "success" | "error">("credentials");
  const [schools, setSchools] = useState<School[]>([]);
  const [selectedSchool, setSelectedSchool] = useState("");
  const [boleta, setBoleta] = useState("");
  const [password, setPassword] = useState("");
  const [captchaSolution, setCaptchaSolution] = useState("");
  const [captchaBase64, setCaptchaBase64] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // Cargar escuelas disponibles al abrir
  useEffect(() => {
    if (open) {
      api
        .get<School[]>("/saes/schools")
        .then((res) => {
          setSchools(res.data);
          if (res.data.length > 0) {
            setSelectedSchool(res.data[0].id);
          }
        })
        .catch((err) => {
          console.error("Error al cargar escuelas:", err);
        });
    }
  }, [open]);

  // Paso 1: Iniciar vinculación (Obtener Captcha)
  const handleStartLink = async () => {
    if (!boleta || !selectedSchool) return;
    setIsLoading(true);
    setErrorMsg("");
    try {
      const res = await api.post("/saes/link/start", {
        boleta,
        school: selectedSchool,
      });
      setCaptchaBase64(res.data.captcha_base64);
      setStep("captcha");
    } catch (err) {
      setErrorMsg(extractErrorMessage(err));
      setStep("error");
    } finally {
      setIsLoading(false);
    }
  };

  // Paso 2: Resolver Captcha y enviar contraseña
  const handleCompleteLink = async () => {
    if (!password || !captchaSolution) return;
    setIsLoading(true);
    setErrorMsg("");
    try {
      await api.post("/saes/link/complete", {
        password,
        captcha_solution: captchaSolution,
      });
      // Forzar sincronización académica inicial
      await api.post("/dashboard/sync");
      setStep("success");
      if (onSuccess) onSuccess();
    } catch (err) {
      setErrorMsg(extractErrorMessage(err));
      setStep("error");
    } finally {
      setIsLoading(false);
    }
  };

  // Recargar captcha si expira o es incorrecto
  const handleRefreshCaptcha = async () => {
    setIsLoading(true);
    try {
      const res = await api.post("/saes/link/start", {
        boleta,
        school: selectedSchool,
      });
      setCaptchaBase64(res.data.captcha_base64);
      setCaptchaSolution("");
    } catch (err) {
      setErrorMsg(extractErrorMessage(err));
      setStep("error");
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setStep("credentials");
    setBoleta("");
    setPassword("");
    setCaptchaSolution("");
    setCaptchaBase64("");
    setErrorMsg("");
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(val) => {
        if (!val) reset();
        onOpenChange(val);
      }}
    >
      <DialogContent className="rounded-clay border-0 bg-white/95 p-6 shadow-clay-lg backdrop-blur-md max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold text-clay-text">
            {step === "credentials" && "Vincula tu cuenta SAES"}
            {step === "captcha" && "Verificación de Seguridad"}
            {step === "success" && "¡Conexión Exitosa!"}
            {step === "error" && "Error de Conexión"}
          </DialogTitle>
          <DialogDescription className="text-sm text-clay-text-secondary">
            {step === "credentials" && "Paso 1 de 2: Selecciona tu plantel e ingresa tu boleta."}
            {step === "captcha" && "Paso 2 de 2: Resuelve el captcha para autorizar el acceso."}
            {step === "success" && "Tus materias y calificaciones se han sincronizado correctamente."}
            {step === "error" && "Hubo un problema al conectar con el SAES."}
          </DialogDescription>
        </DialogHeader>

        {/* PASO 1: Datos de la Escuela y Boleta */}
        {step === "credentials" && (
          <div className="space-y-4 pt-2">
            <div className="space-y-2">
              <Label htmlFor="school-select" className="text-clay-text font-medium">
                Plantel / Escuela
              </Label>
              <Select value={selectedSchool} onValueChange={(val) => setSelectedSchool(val || "")}>
                <SelectTrigger
                  id="school-select"
                  className="rounded-2xl border-0 bg-[#f4f1fa] shadow-clay-input focus:ring-2 focus:ring-clay-primary"
                >
                  <SelectValue placeholder="Selecciona tu escuela" />
                </SelectTrigger>
                <SelectContent className="rounded-clay border-0 bg-white/95 shadow-clay-lg">
                  {schools.map((school) => (
                    <SelectItem key={school.id} value={school.id}>
                      {school.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="boleta-input" className="text-clay-text font-medium">
                Boleta SAES
              </Label>
              <Input
                id="boleta-input"
                type="text"
                pattern="\d*"
                maxLength={10}
                placeholder="Ej. 2024600001"
                value={boleta}
                onChange={(e) => setBoleta(e.target.value.replace(/\D/g, ""))}
                disabled={isLoading}
                className="rounded-2xl border-0 bg-[#f4f1fa] py-6 shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
              />
            </div>

            <Button
              onClick={handleStartLink}
              disabled={isLoading || !boleta || boleta.length < 10}
              className="w-full rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary py-6 text-base font-semibold text-white shadow-clay hover:-translate-y-0.5 active:scale-[0.92] transition-all disabled:opacity-60"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Conectando...
                </>
              ) : (
                "Continuar"
              )}
            </Button>
          </div>
        )}

        {/* PASO 2: Resolver Captcha y Contraseña */}
        {step === "captcha" && (
          <div className="space-y-4 pt-2">
            <div className="flex flex-col items-center justify-center p-3 rounded-2xl bg-[#f4f1fa] shadow-clay-input relative">
              {captchaBase64 ? (
                <img
                  src={`data:image/png;base64,${captchaBase64}`}
                  alt="Captcha SAES"
                  className="h-14 object-contain rounded-lg"
                />
              ) : (
                <div className="h-14 flex items-center justify-center">Cargando captcha...</div>
              )}
              <button
                type="button"
                onClick={handleRefreshCaptcha}
                disabled={isLoading}
                className="absolute right-3 top-3 text-clay-primary-soft hover:text-clay-primary disabled:opacity-50 transition-colors"
                title="Recargar captcha"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              </button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="captcha-solution-input" className="text-clay-text font-medium">
                Escribe el texto de la imagen
              </Label>
              <Input
                id="captcha-solution-input"
                type="text"
                autoComplete="off"
                placeholder="Código captcha"
                value={captchaSolution}
                onChange={(e) => setCaptchaSolution(e.target.value.toUpperCase())}
                disabled={isLoading}
                className="rounded-2xl border-0 bg-[#f4f1fa] py-6 shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password-saes-input" className="text-clay-text font-medium">
                Contraseña del SAES
              </Label>
              <Input
                id="password-saes-input"
                type="password"
                placeholder="••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                className="rounded-2xl border-0 bg-[#f4f1fa] py-6 shadow-clay-input transition-all focus-visible:ring-2 focus-visible:ring-clay-primary focus-visible:ring-offset-2"
              />
            </div>

            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setStep("credentials")}
                disabled={isLoading}
                className="flex-1 rounded-2xl border-clay-border bg-white text-clay-text py-6 hover:bg-clay-surface"
              >
                Atrás
              </Button>
              <Button
                onClick={handleCompleteLink}
                disabled={isLoading || !password || !captchaSolution}
                className="flex-2 w-full rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary py-6 text-base font-semibold text-white shadow-clay hover:-translate-y-0.5 active:scale-[0.92] transition-all disabled:opacity-60"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Vinculando...
                  </>
                ) : (
                  "Vincular cuenta"
                )}
              </Button>
            </div>
          </div>
        )}

        {/* PASO 3: Éxito */}
        {step === "success" && (
          <div className="py-6 text-center space-y-4 pt-2">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 mx-auto shadow-clay">
              <CheckCircle2 className="h-10 w-10" />
            </div>
            <p className="font-bold text-lg text-clay-text">¡Cuenta vinculada!</p>
            <p className="text-sm text-clay-text-secondary">
              Tu boleta <span className="font-mono font-medium text-clay-text">{boleta}</span> ha sido conectada. Ya puedes ver tu kárdex y materias pendientes.
            </p>
            <Button
              onClick={() => onOpenChange(false)}
              className="w-full rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary py-6 text-base font-semibold text-white shadow-clay hover:-translate-y-0.5 active:scale-[0.92] transition-all"
            >
              Ir al Dashboard
            </Button>
          </div>
        )}

        {/* PASO 4: Error */}
        {step === "error" && (
          <div className="py-6 text-center space-y-4 pt-2">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-red-600 mx-auto shadow-clay">
              <AlertCircle className="h-10 w-10" />
            </div>
            <p className="font-bold text-lg text-clay-text">No se pudo vincular</p>
            <p className="text-sm text-red-600 max-w-xs mx-auto">
              {errorMsg}
            </p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setStep("credentials")}
                className="flex-1 rounded-2xl border-clay-border bg-white text-clay-text py-6"
              >
                Ajustar boleta
              </Button>
              <Button
                onClick={() => {
                  setStep("captcha");
                  handleRefreshCaptcha();
                }}
                className="flex-1 rounded-2xl bg-gradient-to-r from-clay-primary-soft to-clay-primary py-6 text-white font-semibold"
              >
                Reintentar
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
